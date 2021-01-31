
import os,sys,math,re,glob,json,copy
from array import array
import plotter

import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)

colors = [ROOT.kBlack, ROOT.kBlue, ROOT.kRed, ROOT.kOrange, ROOT.kGreen, ROOT.kCyan]


def rebin(h, bins):

    mybins = array('d', newbins)
    h1 = h.Rebin(len(mybins)-1, h.GetName(), mybins)
    return h1

def getHists(tag):

    global fIn_FAST, fIn_FULL
    
    h_fast = fIn_FAST.Get(tag)
    h_fast.SetTitle("fast_" + h_fast.GetTitle())
    
    h_full = fIn_FULL.Get(tag)
    h_full.SetTitle("full_" + h_full.GetTitle())
    
    return h_fast, h_full
    
    
def getHist(tag):

    global fIn_FAST, fIn_FULL
    
    h_fast = fIn_FAST.Get(tag)
    h_fast.SetTitle("fast_" + h_fast.GetTitle())
    
    h_full = fIn_FULL.Get(tag)
    h_full.SetTitle("full_" + h_full.GetTitle())
    
    return h_fast, h_full


def plot(runs, labels, outDir, tag, xMin, xMax, yMin, yMax, xLabel, yLabel, rebin=1, logY=False):
    
    if not os.path.exists(outDir): os.makedirs(outDir)
    
    hists = []
    
    for i, run in enumerate(runs):
    
        fIn = ROOT.TFile(run)
        hist = fIn.Get(tag)
        hist = copy.deepcopy(hist)
        fIn.Close()
        hist.SetTitle("%s_%s" % (hist.GetTitle(), i))
        
        if isinstance(rebin, int): hist = hist.Rebin(rebin)
        else: hist = hist.Rebin(rebin)

        hists.append(hist)
        
    cfg = {

        'logy'              : logY,
        'logx'              : False,
    
        'xmin'              : xMin,
        'xmax'              : xMax,
        'ymin'              : yMin,
        'ymax'              : yMax,
        
        'xtitle'            : xLabel,
        'ytitle'            : yLabel,
        'analysis'          : "",
        
        'topLeft'           : "#bf{CMS} #scale[0.7]{#it{Simulation}}",
        'topRight'          : "13 TeV, pp #rightarrow t#bar{t}",
    }
    
    
    plotter.cfg = cfg
    canvas = plotter.canvas()
    
    dummy = plotter.dummy()
    dummy.Draw("HIST")
    
    
    leg = ROOT.TLegend(0.5, 0.9-0.05*len(runs), 0.95, 0.9)
    leg.SetHeader("CMSSW_10_6_20")
    leg.SetBorderSize(0)
    leg.SetFillStyle(0) #1001
    leg.SetFillColor(0)
    leg.SetTextSize(0.03)
    leg.SetMargin(0.15)
    
    for i, run in enumerate(runs):
        hists[i].SetLineStyle(1)
        hists[i].SetLineWidth(3)
        hists[i].SetLineColor(colors[i])
        hists[i].Draw("HIST SAME")
        leg.AddEntry(hists[i], labels[i], "L")

    leg.Draw("SAME")

    canvas.SetGrid()
    canvas.Modify()
    canvas.Update()

    plotter.aux()

    
    ROOT.gPad.SetTicks()
    ROOT.gPad.RedrawAxis()

    canvas.SaveAs("%s/%s.png" % (outDir, tag))  
    canvas.SaveAs("%s/%s.pdf" % (outDir, tag))  
    


def plotRatio(outDir, tag, xMin, xMax, yMin, yMax, xLabel, yLabel, rebin=1, logY=False):

    if not os.path.exists(outDir): os.makedirs(outDir)
    
    h_fast, h_full = getHists(tag)
    
    if isinstance(rebin, int):
    
        h_fast = h_fast.Rebin(rebin)
        h_full.Rebin(rebin)
        
    else:
    
        h_fast = rebin(h_fast, rebin)
        h_full = rebin(h_full, rebin)
        
    h_ratio = h_full.Clone("ratio")
    h_ratio.Divide(h_fast)

    cfg = {

        'logy'              : logY,
        'logx'              : False,
    
        'xmin'              : xMin,
        'xmax'              : xMax,
        'ymin'              : yMin,
        'ymax'              : yMax,
        
        'xtitle'            : xLabel,
        'ytitle'            : yLabel,

        
        'topLeft'           : "#bf{CMS} #scale[0.7]{#it{Simulation}}",
        'topRight'          : "13 TeV, pp #rightarrow t#bar{t}",
        
        # ratio bar 
        'ratiofraction'     : 0.3,
        'ytitleR'           : "Full/Fast",
        'yminR'             : 0.2,
        'ymaxR'             : 1.8,
    }
    
    
    plotter.cfg = cfg
    
    canvas, padT, padB = plotter.canvasRatio()
    dummyT, dummyB = plotter.dummyRatio()
            
            
    ## main panel
    canvas.cd()
    padT.Draw()
    padT.cd()
    dummyT.Draw("HIST")
    
    
    
    leg = ROOT.TLegend(0.5, 0.7, 0.95, 0.9)
    leg.SetHeader("FastSim (CMSSW_10_6_20)")
    leg.SetBorderSize(0)
    leg.SetFillStyle(0) #1001
    leg.SetFillColor(0)
    leg.SetTextSize(0.05)
    leg.SetMargin(0.15)
    

    h_fast.SetLineStyle(1)
    h_fast.SetLineWidth(3)
    h_fast.SetLineColor(ROOT.kBlue)
    h_fast.Draw("HIST SAME")
    leg.AddEntry(h_fast, "Fast sim", "L")
    
    h_full.SetLineStyle(1)
    h_full.SetLineWidth(3)
    h_full.SetLineColor(ROOT.kRed)
    h_full.Draw("HIST SAME")
    leg.AddEntry(h_full, "Full sim", "L")
    
    leg.Draw("same")
    
    plotter.auxRatio()
    padT.SetGrid()
    
    ROOT.gPad.SetTickx()
    ROOT.gPad.SetTicky()
    ROOT.gPad.RedrawAxis()  
    
    
    ## ratio panel
    canvas.cd()
    padB.Draw()
    padB.SetFillStyle(0)

    padB.cd()
    dummyB.Draw("HIST")
    
    line = ROOT.TLine(float(cfg['xmin']), 1, float(cfg['xmax']), 1)
    line.SetLineColor(ROOT.kBlue+2)
    line.SetLineWidth(2)
    line.Draw("SAME")    
 
 
    h_ratio.SetMarkerStyle(20)
    h_ratio.SetMarkerSize(0.7)
    h_ratio.SetMarkerColor(ROOT.kBlack)
    h_ratio.SetLineColor(ROOT.kBlack)
    h_ratio.SetLineWidth(2)
    h_ratio.SetFillColor(ROOT.kBlack)
    h_ratio.SetFillStyle(3004)    
    h_ratio.Draw("P SAME") # E2 SAME
    
         

    
    canvas.Modify()
    canvas.Update()
   
    ROOT.gPad.SetTickx()
    ROOT.gPad.SetTicky()
    ROOT.gPad.RedrawAxis()
    
    canvas.SaveAs("%s/%s.png" % (outDir, tag))  
    canvas.SaveAs("%s/%s.pdf" % (outDir, tag))  
    canvas.Close()
    


if __name__ == "__main__":


    if True:
    
        runs = ["root/ttbar_fast_pu0.root", "root/ttbar_fast_pu50.root", "root/ttbar_fast_pu150.root"]
        labels = ["FastSim PU0", "FastSim PU50", "FastSim PU150"]
        outDir = "plots/ttbar_fastsim_pu/"
        
        plot(runs, labels, outDir, "leading_mu_pt_reco", 0, 500, 10, 1e4, "Leading muon PT (GeV)", "Events", logY=True, rebin=10)
        
        plot(runs, labels, outDir, "leading_mu_pt_reco", 0, 500, 10, 1e4, "Leading muon PT (GeV)", "Events", logY=True, rebin=10)
        plot(runs, labels, outDir, "leading_mu_eta_reco", -3, 3, 10, 1e4, "Leading muon ETA", "Events", logY=True)
        plot(runs, labels, outDir, "leading_mu_res", -0.5, 0.5, 10, 1e4, "Leading muon resolution", "Events", logY=True)
        
        
        plot(runs, labels, outDir, "leading_el_pt_reco", 0, 500, 10, 1e4, "Leading electron PT (GeV)", "Events", logY=True, rebin=5)
        plot(runs, labels, outDir, "leading_el_eta_reco", -3, 3, 10, 1e4, "Leading electron ETA", "Events", logY=True)
        plot(runs, labels, outDir, "leading_el_res", -0.5, 0.5, 10, 1e4, "Leading electron resolution", "Events", logY=True)
        
        
        plot(runs, labels, outDir, "jet_pt", 0, 500, 100, 1e5, "Jet PT (GeV)", "Events", logY=True, rebin=5)
        plot(runs, labels, outDir, "jet_pt_uncorr", 0, 500, 100, 1e5, "Uncorrected jet PT  (GeV)", "Events", logY=True, rebin=5)
        plot(runs, labels, outDir, "jet_eta", -3, 3, 100, 1e5, "Jet ETA", "Events", logY=True)
        
        plot(runs, labels, outDir, "njets", 0, 15, 100, 1e6, "Number of jets", "Events", logY=True)
        plot(runs, labels, outDir, "nbjets", 0, 10, 100, 1e6, "Number of b-tagged jets", "Events", logY=True)
        plot(runs, labels, outDir, "jet_csv", 0, 1, 100, 1e5, "CSV discriminant", "Events", logY=True)
        plot(runs, labels, outDir, "jet_deepcsv", 0, 1, 100, 1e5, "deepCSV discriminant", "Events", logY=True)
        
        
        plot(runs, labels, outDir, "met_reco", 0, 500, 100, 1e5, "MET (GeV)", "Events", logY=True, rebin=5)
        plot(runs, labels, outDir, "met_reco_uncorr", 0, 500, 100, 1e5, "Uncorrected MET (GeV)", "Events", logY=True, rebin=5)
        plot(runs, labels, outDir, "met_sumet_reco", 0, 5000, 100, 1e4, "sumET (GeV)", "Events", logY=True, rebin=20)
        
        
        plot(runs, labels, outDir, "npv", 0, 200, 100, 1e6, "Number of primary vertices", "Events", logY=True)
        plot(runs, labels, outDir, "pv_z", 0, 20, 100, 1e6, "Primary vertex z position (cm)", "Events", logY=True)
        plot(runs, labels, outDir, "pu_numinteractions", 0, 200, 100, 1e6, "<PU> interactions", "Events", logY=True)

    if True:
    
        # comparison fast-fullsim zero pileup
        outDir = "plots/ttbar_pu0/"
        fIn_FAST = ROOT.TFile("root/ttbar_fast_pu0.root")
        fIn_FULL = ROOT.TFile("root/ttbar_full_pu0.root")
        
        # comparison fast-fullsim 50 pileup
        outDir = "plots/ttbar_pu50/"
        fIn_FAST = ROOT.TFile("root/ttbar_fast_pu50.root")
        fIn_FULL = ROOT.TFile("root/ttbar_full_pu50.root")
        

        plotRatio(outDir, "leading_mu_pt_reco", 0, 500, 10, 1e4, "Leading muon PT (GeV)", "Events", logY=True, rebin=10)
        plotRatio(outDir, "leading_mu_eta_reco", -3, 3, 10, 1e4, "Leading muon ETA", "Events", logY=True)
        plotRatio(outDir, "leading_mu_res", -0.5, 0.5, 10, 1e4, "Leading muon resolution", "Events", logY=True)
        
        
        plotRatio(outDir, "leading_el_pt_reco", 0, 500, 10, 1e4, "Leading electron PT (GeV)", "Events", logY=True, rebin=5)
        plotRatio(outDir, "leading_el_eta_reco", -3, 3, 10, 1e4, "Leading electron ETA", "Events", logY=True)
        plotRatio(outDir, "leading_el_res", -0.5, 0.5, 10, 1e4, "Leading electron resolution", "Events", logY=True)
        
        
        plotRatio(outDir, "jet_pt", 0, 500, 100, 1e5, "Jet PT (GeV)", "Events", logY=True, rebin=5)
        plotRatio(outDir, "jet_pt_uncorr", 0, 500, 100, 1e5, "Uncorrected jet PT  (GeV)", "Events", logY=True, rebin=5)
        plotRatio(outDir, "jet_eta", -3, 3, 100, 1e5, "Jet ETA", "Events", logY=True)
        
        plotRatio(outDir, "njets", 0, 15, 100, 1e6, "Number of jets", "Events", logY=True)
        plotRatio(outDir, "nbjets", 0, 10, 100, 1e6, "Number of b-tagged jets", "Events", logY=True)
        plotRatio(outDir, "jet_csv", 0, 1, 100, 1e5, "CSV discriminant", "Events", logY=True)
        plotRatio(outDir, "jet_deepcsv", 0, 1, 100, 1e5, "deepCSV discriminant", "Events", logY=True)
        
        
        plotRatio(outDir, "met_reco", 0, 500, 100, 1e5, "MET (GeV)", "Events", logY=True, rebin=10)
        plotRatio(outDir, "met_sumet_reco", 0, 5000, 100, 1e4, "sumET (GeV)", "Events", logY=True, rebin=20)
        plotRatio(outDir, "met_sumet_gen", 0, 5000, 100, 1e4, "sumET (GeV)", "Events", logY=True, rebin=20)
        #plotRatio(outDir, "met_gen", 0, 500, 100, 1e5, "Jet pT (reco)", "Events", logY=True, rebin=5)
        plotRatio(outDir, "met_reco_uncorr", 0, 500, 100, 1e5, "Uncorrected MET (GeV)", "Events", logY=True, rebin=5)
        
        
        plotRatio(outDir, "npv", 0, 10, 100, 1e6, "Number of primary vertices", "Events", logY=True)
        plotRatio(outDir, "pv_z", 0, 20, 100, 1e5, "Primary vertex z position (cm)", "Events", logY=True)
        plotRatio(outDir, "pu_numinteractions", 0, 100, 100, 1e6, "<PU> interactions", "Events", logY=True)
        
        


        

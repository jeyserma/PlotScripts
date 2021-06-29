
import sys,array,copy, math
import ROOT
ROOT.gROOT.SetBatch()
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)


def Rebin(h, newbins):
    
    mybins = array.array('d', newbins)
    h1 = h.Rebin(len(mybins)-1, h.GetName(), mybins)
    return h1

class AutoRebin:
    
    h = None        # backgrounds
    h_sig = None    # signal
    maxStat = 0.3
    maxSigStat = 0.3
    
    binMin = 0
    binMax = 0
    
    def __init__(self, h, h_sig, maxStat, maxSigStat = 0.2):
        
        self.h = h
        self.maxStat = maxStat
        self.maxSigStat = maxSigStat
        self.h_sig = h_sig
        
        self.binMin = float(self.h.GetBinLowEdge(1)) # min bin
        self.binMax = float(self.h.GetBinLowEdge(h.GetNbinsX()+1)) # max bin
        

    def getHist(self):
        
        return self.h


    def mergeCriteria(self, i):
        
        if self.h.GetBinContent(i) <= 0 or self.h.GetBinError(i) / self.h.GetBinContent(i) > self.maxStat or self.h_sig.GetBinContent(i) <= 0 or self.h_sig.GetBinError(i) / self.h_sig.GetBinContent(i) > self.maxSigStat: return True
        else: return False


    # Recursive rebin function
    def directionalRebin(self, direction = ""):

        if direction == "":
            
            self.directionalRebin("right")
            self.directionalRebin("left")
            return
            
        if direction == "left"  : r = range(1, self.h.GetNbinsX()) # do not include the last bin
        if direction == "right" : r = reversed(range(2, self.h.GetNbinsX()+1)) # start from the right bin towards the left (do not include the zero!)

        for i in r:

            if self.mergeCriteria(i): 

                if direction == "left":
                    
                    self.mergeBins(i+1)
                    self.directionalRebin(direction) 
                    return
                
                else : 

                    self.mergeBins(i)
                    self.directionalRebin(direction)
                    return
              
        return
    
    def rebin(self):

        # first binning on bkg
        self.directionalRebin()


    # function which merges bin i with the left adjecent bin
    def mergeBins(self, i):

        '''
        arr = self.getBinArray()


        ARR INDEX	 0  1    2    3     4     5     6
                    [0, 100, 500, 1000, 2000, 5000, 8000] 
        BIN NUMBER	  1    2    3     4     5     6
  

        # i represents the bin number, so do i-1

        # construct array of bins from the histo
        arr_new = []
        for j in range(0, len(arr)):

            if j == i-1: continue
            arr_new.append(arr[j])

        # merge and return
        mybins = array.array('d', arr_new)
        self.h = self.h.Rebin(len(mybins)-1, self.h.GetName(), mybins) 
        self.h_sig = self.h_sig.Rebin(len(mybins)-1, self.h_sig.GetName(), mybins) 
        '''
 
        arr = self.getBinArray()

        '''
        ARR INDEX	 0  1    2    3     4     5     6
                    [0, 100, 500, 1000, 2000, 5000, 8000] 
        BIN NUMBER	  1    2    3     4     5     6
        '''

        # i represents the bin number, so do i-1

        # construct array of bins from the histo
        arr_new = []
        for j in range(0, len(arr)):

            if j == i-1: continue
            arr_new.append(arr[j])

        # merge and return
        mybins = array.array('d', arr_new)
        
        #self.h = self.h.Rebin(len(mybins)-1, self.h.GetName(), mybins)
        

        name = self.h.GetName()
        self.h.SetName("tmpp")
        tmp = self.h.Rebin(len(mybins)-1, name, mybins)
        self.h.Delete() # necessary to reduce memory
        self.h = tmp
        
        name = self.h_sig.GetName()
        self.h_sig.SetName("tmpp")
        tmp = self.h_sig.Rebin(len(mybins)-1, name, mybins)
        self.h_sig.Delete() # necessary to reduce memory
        self.h_sig = tmp
        


    def getBinArray(self):

        ret = [self.binMin]
        for i in range(2, self.h.GetNbinsX()+1): 

            x = float(self.h.GetBinLowEdge(i))
            ret.append(x)
            
        ret.append(self.binMax)
        return ret



if __name__ == "__main__":

    # generate random background (poly) and signal (Gauss)
    bkg = ROOT.TF1("bkg", "exp(-0.5*((x-4.)/1.)**2)", 0, 10)
    h_bkg = ROOT.TH1D("h_bkg", "h_bkg", 1000, 0, 10)
    h_bkg.FillRandom("bkg", 5000)


    sig = ROOT.TF1("sig", "exp(-0.5*((x-6.)/1.)**2)", 0, 10)
    h_sig = ROOT.TH1D("h_sig", "h_sig", 1000, 0, 10)
    h_sig.FillRandom("sig", 5000)

    canvas = ROOT.TCanvas("c", "c", 600, 600)
    h_sig.SetLineColor(ROOT.kRed)
    h_sig.Draw("HIST")
    h_bkg.Draw("HIST SAME")
    canvas.SaveAs("binning.png")
    canvas.Clear()
    
    # do auto-rebinning
    b = AutoRebin(h_bkg.Clone("b_bkg_copy"), h_sig.Clone("h_sig_copy"), 0.2, 0.2) # need to pass copies, to avoid memory overwrite
    b.rebin()
    binning = b.getBinArray() # returns array of bins
                
    print binning
    
    h_sig = Rebin(h_sig, binning)
    h_bkg = Rebin(h_bkg, binning)
   
    h_bkg.Draw("HIST")
    h_sig.SetLineColor(ROOT.kRed)
    h_sig.Draw("HIST SAME")
    
    canvas.SaveAs("binning_rebin.png")
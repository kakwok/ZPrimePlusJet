import ROOT
from ROOT import TFile, TTree, TChain, gPad, gDirectory
from multiprocessing import Process
from optparse import OptionParser
from operator import add
import math
import sys
import time
import array
import glob
import os
from plotHelpers import *
from sampleContainer import *
DBTMIN=-99
#

def makePlots(hb,style,odir,lumi,ofile,canvases):
    hist_pass_cat = []
    hist_fail_cat = []
    msd_binBoundaries=[]
    for i in range(0,24):	
        msd_binBoundaries.append(40.+i*7)
    ptBinBoundaries = []
    ptBinBoundaries.append(hb['QCD']['h_msd_v_pt_ak8_topR6_N2_pass'].GetYaxis().GetBinLowEdge(1))
    for j in range(1,hb['QCD']['h_msd_v_pt_ak8_topR6_N2_fail'].GetNbinsY()+1):
        hist_pass = ROOT.TH1F('h_QCD_msd_ak8_topR6_N2_pass_cat%i'%j, 'h_QCD_msd_ak8_topR6_N2_pass_cat%i'%j, len(msd_binBoundaries)-1, array.array('d',msd_binBoundaries))
        hist_fail = ROOT.TH1F('h_QCD_msd_ak8_topR6_N2_fail_cat%i'%j, 'h_QCD_msd_ak8_topR6_N2_fail_cat%i'%j, len(msd_binBoundaries)-1, array.array('d',msd_binBoundaries))
        hist_pass.GetXaxis().SetTitle(hb['QCD']['h_msd_v_pt_ak8_topR6_N2_pass'].GetXaxis().GetTitle())
        hist_fail.GetXaxis().SetTitle(hb['QCD']['h_msd_v_pt_ak8_topR6_N2_fail'].GetXaxis().GetTitle())
        ptBinBoundaries.append(hb['QCD']['h_msd_v_pt_ak8_topR6_N2_pass'].GetYaxis().GetBinUpEdge(j))
        for i in range(1,hb['QCD']['h_msd_v_pt_ak8_topR6_N2_fail'].GetNbinsX()+1):
            hist_pass.SetBinContent(i,hb['QCD']['h_msd_v_pt_ak8_topR6_N2_pass'].GetBinContent(i,j))
            hist_pass.SetBinError(i,hb['QCD']['h_msd_v_pt_ak8_topR6_N2_pass'].GetBinError(i,j))
            hist_fail.SetBinContent(i,hb['QCD']['h_msd_v_pt_ak8_topR6_N2_fail'].GetBinContent(i,j))
            hist_fail.SetBinError(i,hb['QCD']['h_msd_v_pt_ak8_topR6_N2_fail'].GetBinError(i,j))
        hist_pass_cat.append(hist_pass)
        hist_fail_cat.append(hist_fail)

    c = makeCanvasRatio(hb['QCD']['h_msd_ak8_topR6_N2_fail'],hb['QCD']['h_msd_ak8_topR6_N2_pass'],['QCD fail, p_{T} > %i GeV'%ptBinBoundaries[0],'QCD pass, p_{T} > %i GeV'%ptBinBoundaries[0]],[ROOT.kBlue,ROOT.kBlack],style,'ratio_msd_ak8_topR6_N2',odir,lumi,ofile)
    canvases.append(c)	
    c1, f2params = makeCanvasRatio2D(hb['QCD']['h_msd_v_pt_ak8_topR6_N2_fail'],hb['QCD']['h_msd_v_pt_ak8_topR6_N2_pass'],['QCD fail, p_{T} > 500 GeV','QCD pass, p_{T}>500 GeV'],[ROOT.kBlue,ROOT.kBlack],style,'ratio_msd_v_pt_ak8_topR6_N2',odir,lumi,ofile)
    canvases.append(c1)
    for i in range(1,len(ptBinBoundaries)):
        c = makeCanvasRatio(hist_fail_cat[i-1],hist_pass_cat[i-1],['QCD fail, %i < p_{T} < %i GeV'%(ptBinBoundaries[i-1],ptBinBoundaries[i]),'QCD pass, %i < p_{T} < %i GeV'%(ptBinBoundaries[i-1],ptBinBoundaries[i])],[ROOT.kBlue,ROOT.kBlack],style,'ratio_msd_ak8_topR6_N2_cat%i'%i,odir,lumi,ofile,(ptBinBoundaries[i-1]+ptBinBoundaries[i])/2.,f2params)
        canvases.append(c)
    
##############################################################################
def main(options,args,outputExists):
    #idir = "/eos/uscms/store/user/lpchbb/ggHsample_V11/sklim-v0-28Oct/"
    #odir = "plots_2016_10_31/"
    #idir = options.idir
    idir = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v12.08-HWW/norm/'
    idir_hadd = 'root://cmseos.fnal.gov//eos/uscms/store/user/lpcbacon/dazsle/zprimebits-v12.08-HWW/hadd/'
    odir = options.odir
    lumi = options.lumi
    isData = options.isData
    muonCR = options.muonCR

    
    legname = {'ggHbb': 'ggH(b#bar{b})',
               'Hbb': 'H(b#bar{b})',
               'VBFHbb':'VBF H(b#bar{b})',
               'VHbb': 'VH(b#bar{b})',
	       'ttHbb': 't#bar{t}H(b#bar{b})',
               'Diboson': 'VV(4q)',
               'SingleTop': 'single-t',
               'DY': 'Z+jets',
               'W': 'W+jets',
               'TTbar': 't#bar{t}+jets',        
               'TTbar1Mu': 't#bar{t}+jets, 1#mu',  
               'TTbar1Ele': 't#bar{t}+jets, 1e',        
               'TTbar1Tau': 't#bar{t}+jets, 1#tau',        
               'TTbar0Lep': 't#bar{t}+jets, 0l',        
               'QCD': 'QCD',
		       'data': 'JetHT data',
               'muon': 'SingleMuon data',
               'Phibb50': '#Phi(b#bar{b}), 50 GeV',
               'Phibb75': '#Phi(b#bar{b}), 75 GeV',
               'Phibb150': '#Phi(b#bar{b}), 150 GeV',
               'Phibb250': '#Phi(b#bar{b}), 250 GeV'               
               }

    if isData and muonCR:
        legname['data'] = 'SingleMuon data'
        
    tfiles = {
        'QCD_HT': [
            #idir+'/QCD_HT100to200_13TeV_8X_1000pb_weighted.root',
            #idir+'/QCD_HT200to300_13TeV_8X_1000pb_weighted.root',
            idir+'/QCD_HT300to500_13TeV_8X_1000pb_weighted.root',
            idir+'/QCD_HT500to700_13TeV_ext_8X_1000pb_weighted.root',
            idir+'/QCD_HT1000to1500_13TeV_8X_1000pb_weighted.root',
            idir+'/QCD_HT1500to2000_13TeV_ext_8X_1000pb_weighted.root',
            idir+'/QCD_HT2000toInf_13TeV_ext_8X_1000pb_weighted.root'
            ],
        'QCD_HT700to1000': [
            idir_hadd+'/QCD_HT700to1000_13TeV_8X_0.root',
            idir_hadd+'/QCD_HT700to1000_13TeV_8X_1.root',
            idir_hadd+'/QCD_HT700to1000_13TeV_8X_2.root',
            idir_hadd+'/QCD_HT700to1000_13TeV_8X_3.root',
            idir_hadd+'/QCD_HT700to1000_13TeV_8X_4.root',
            idir_hadd+'/QCD_HT700to1000_13TeV_8X_5.root',
            idir_hadd+'/QCD_HT700to1000_13TeV_8X_6.root'
            ]
        }

    color = {'ggHbb': ROOT.kAzure+1,
             'Hbb': ROOT.kRed,
             'VHbb': ROOT.kTeal+1,
             'VBFHbb': ROOT.kBlue-10,
		     'Phibb50': ROOT.kBlue-1,
             'Phibb75': ROOT.kAzure+1,
		     'Phibb150': ROOT.kTeal+1,
		     'Phibb250': ROOT.kMagenta+1,
		     'ttHbb': ROOT.kBlue-1,
             'Diboson': ROOT.kOrange,
             'SingleTop': ROOT.kRed-2,
             'DY':  ROOT.kRed+1,
             'W':  ROOT.kGreen+2,
             'TTbar':  ROOT.kGray,
             'TTbar1Mu':  ROOT.kViolet,
             'TTbar1Ele':  ROOT.kSpring,
             'TTbar1Tau':  ROOT.kOrange+2,
             'TTbar0Lep':  ROOT.kGray,
             'QCD': ROOT.kBlue+2,
		     'data':ROOT.kBlack,
		     'muon':ROOT.kBlack
            }

    style = {'Hbb': 1,
             'ggHbb': 2,             
		     'Phibb50': 2,
             'Phibb75': 3,
		     'Phibb150': 4,
		     'Phibb250': 5,
             'VBFHbb': 3,
		     'VHbb': 4,
		     'ttHbb': 5,
             'Diboson': 1,
             'SingleTop': 1,
             'DY': 1,
             'W': 1,
             'TTbar': 1,
             'TTbar1Mu': 1,
             'TTbar1Ele': 1,
             'TTbar1Tau': 1,
             'TTbar0Lep': 1,
             'QCD': 1,
             'data': 1,
		     'muon':1
            }

        
    canvases = []
    plots = ['h_msd_ak8_topR6_N2_pass','h_msd_ak8_topR6_N2_fail','h_msd_v_pt_ak8_topR6_N2_pass','h_msd_v_pt_ak8_topR6_N2_fail',
             'h_pt_ak8',
             'h_msd_ak8',
             'h_dbtag_ak8']

    if not outputExists: 
        print "Backgrounds..."
        bkgSamples = {}    
        bkgSamples['QCD_HT'] = sampleContainer('QCD_HT',tfiles['QCD_HT'], sf=1, 
                                               DBTAGCUTMIN=DBTMIN, lumi=lumi, isData=False,
                                               fillCA15=False, cutFormula = '1', minBranches =False, 
                                               iSplit = options.iSplit, maxSplit = options.maxSplit, treeName = 'otree', 
                                               doublebName = options.doublebName, doublebCut = options.doublebCut)
        bkgSamples['QCD_HT700to1000'] = sampleContainer('QCD_HT700to1000',tfiles['QCD_HT700to1000'], sf=1, 
                                                        DBTAGCUTMIN=DBTMIN, lumi=lumi*1000.*6831./1.55837e+07, isData=False,
                                                        fillCA15=False, cutFormula = '1', minBranches=False, 
                                                        iSplit = options.iSplit, maxSplit = options.maxSplit, treeName = 'Events',
                                                        doublebName = options.doublebName, doublebCut = options.doublebCut)
        #bkgSamples['TTbar1Mu']  = sampleContainer('TTbar1Mu',tfiles['TTbar'], 1, lumi, False, False, 'genMuFromW==1&&genEleFromW+genTauFromW==0')
        #bkgSamples['TTbar1Ele']  = sampleContainer('TTbar1Ele',tfiles['TTbar'], 1, lumi, False, False, 'genEleFromW==1&&genMuFromW+genTauFromW==0')
        #bkgSamples['TTbar1Tau']  = sampleContainer('TTbar1Tau',tfiles['TTbar'], 1, lumi, False, False, 'genTauFromW==1&&genEleFromW+genMuFromW==0')
        #bkgSamples['TTbar0Lep']  = sampleContainer('TTbar0Lep',tfiles['TTbar'], 1, lumi, False, False, 'genMuFromW+genEleFromW+genTauFromW==0')
        #bkgSamples['TTbar']  = sampleContainer('TTbar',tfiles['TTbar'], 1, lumi)

        ofile = ROOT.TFile.Open(odir+'/Ratios_1000pb_weighted_%s.root '%options.iSplit,'recreate')

        hb = {}
        for process, s in bkgSamples.iteritems():
            hb[process] = {}
            for plot in plots:
                hb[process][plot] = getattr(s,plot)

        hb['QCD'] = {}
        for plot in plots:
            hb['QCD'][plot] = hb['QCD_HT'][plot].Clone(hb['QCD_HT'][plot].GetName().replace('QCD_HT','QCD'))
            hb['QCD'][plot].Add(hb['QCD_HT700to1000'][plot])
            
        makePlots(hb,style,odir,lumi,ofile,canvases)
        
        ofile.cd()
        for proc, hDict in hb.iteritems():
            for plot, h in hDict.iteritems():
                h.Write()
        ofile.Close()
    else:
        
        ofile = ROOT.TFile.Open(odir+'/Ratios_1000pb_weighted.root','read')

        
        
        hb = {}
        for process in ['QCD_HT','QCD_HT700to1000']:
            hb[process] = {}
            for plot in plots:
                hb[process][plot] = ofile.Get(plot.replace('h_','h_%s_'%process))
        hb['QCD'] = {}
        for plot in plots:
            hb['QCD'][plot] = hb['QCD_HT'][plot].Clone(hb['QCD_HT'][plot].GetName().replace('QCD_HT','QCD'))
            hb['QCD'][plot].Add(hb['QCD_HT700to1000'][plot])
                
        hb['QCD']['h_msd_v_pt_ak8_topR6_N2_fail'].SetBinContent(23,1,0)
        hb['QCD']['h_msd_v_pt_ak8_topR6_N2_pass'].SetBinContent(23,1,0)
        hb['QCD']['h_msd_v_pt_ak8_topR6_N2_fail'].SetBinContent(22,1,0)
        hb['QCD']['h_msd_v_pt_ak8_topR6_N2_pass'].SetBinContent(22,1,0)
        hb['QCD']['h_msd_v_pt_ak8_topR6_N2_fail'].SetBinContent(21,1,0)
        hb['QCD']['h_msd_v_pt_ak8_topR6_N2_pass'].SetBinContent(21,1,0)
        hb['QCD']['h_msd_v_pt_ak8_topR6_N2_fail'].SetBinContent(20,1,0)
        hb['QCD']['h_msd_v_pt_ak8_topR6_N2_pass'].SetBinContent(20,1,0)
        hb['QCD']['h_msd_v_pt_ak8_topR6_N2_fail'].SetBinContent(19,1,0)
        hb['QCD']['h_msd_v_pt_ak8_topR6_N2_pass'].SetBinContent(19,1,0)
        hb['QCD']['h_msd_v_pt_ak8_topR6_N2_fail'].SetBinContent(23,2,0)
        hb['QCD']['h_msd_v_pt_ak8_topR6_N2_pass'].SetBinContent(23,2,0)
        hb['QCD']['h_msd_v_pt_ak8_topR6_N2_fail'].SetBinContent(22,2,0)
        hb['QCD']['h_msd_v_pt_ak8_topR6_N2_pass'].SetBinContent(22,2,0)
        hb['QCD']['h_msd_v_pt_ak8_topR6_N2_fail'].SetBinContent(21,2,0)
        hb['QCD']['h_msd_v_pt_ak8_topR6_N2_pass'].SetBinContent(21,2,0)

        # fix high bin
        #ave = (hb['QCD']['h_msd_v_pt_ak8_topR6_N2_fail'].GetBinContent(12,4)+hb['QCD']['h_msd_v_pt_ak8_topR6_N2_fail'].GetBinContent(14,4))/2.
        #hb['QCD']['h_msd_v_pt_ak8_topR6_N2_fail'].SetBinContent(13,4,ave)
        #ave = (hb['QCD']['h_msd_v_pt_ak8_topR6_N2_fail'].GetBinError(12,4)+hb['QCD']['h_msd_v_pt_ak8_topR6_N2_fail'].GetBinError(14,4))/2.
        #hb['QCD']['h_msd_v_pt_ak8_topR6_N2_fail'].SetBinError(13,4,ave)
                
        hb['QCD']['h_msd_v_pt_ak8_topR6_N2_pass'].Scale(1./hb['QCD']['h_msd_v_pt_ak8_topR6_N2_pass'].Integral())
        hb['QCD']['h_msd_v_pt_ak8_topR6_N2_fail'].Scale(1./hb['QCD']['h_msd_v_pt_ak8_topR6_N2_fail'].Integral())
        hb['QCD']['h_msd_ak8_topR6_N2_pass'].Scale(1./hb['QCD']['h_msd_ak8_topR6_N2_pass'].Integral())
        hb['QCD']['h_msd_ak8_topR6_N2_fail'].Scale(1./hb['QCD']['h_msd_ak8_topR6_N2_fail'].Integral())
                
        makePlots(hb,style,odir,lumi,ofile,canvases)
        
        


##----##----##----##----##----##----##
if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option('-b', action='store_true', dest='noX', default=False, help='no X11 windows')
    parser.add_option("--lumi", dest="lumi", default = 30,type=float,help="luminosity", metavar="lumi")
    parser.add_option('-i','--idir', dest='idir', default = 'data/',help='directory with data', metavar='idir')
    parser.add_option('-o','--odir', dest='odir', default = 'plots/',help='directory to write plots', metavar='odir')
    parser.add_option('-s','--isData', action='store_true', dest='isData', default =False,help='signal comparison', metavar='isData')
    parser.add_option('-m','--muonCR', action='store_true', dest='muonCR', default =False,help='for muon CR', metavar='muonCR')
    parser.add_option("--max-split", dest="maxSplit", default=1, type="int", help="max number of jobs", metavar="maxSplit")
    parser.add_option("--i-split"  , dest="iSplit", default=0, type="int", help="job number", metavar="iSplit")
    parser.add_option("--double-b-name"  , dest="doublebName", default="AK8Puppijet0_deepdoublecsv", help="double-b name", metavar="doublebName")
    parser.add_option("--double-b-cut"  , dest="doublebCut", default=0.9, type="float", help="double-b cut", metavar="doublebCut")

    (options, args) = parser.parse_args()

     
    import tdrstyle
    tdrstyle.setTDRStyle()
    ROOT.gStyle.SetPadTopMargin(0.10)
    ROOT.gStyle.SetPadLeftMargin(0.16)
    ROOT.gStyle.SetPadRightMargin(0.10)
    ROOT.gStyle.SetPaintTextFormat("1.1f")
    ROOT.gStyle.SetOptFit(0000)
    ROOT.gStyle.SetPalette(ROOT.kBird)
    #ROOT.gStyle.SetPalette(1)
    ROOT.gROOT.SetBatch()

    ## stops = [0.0000, 0.1250, 0.2500, 0.3750, 0.5000, 0.6250, 0.7500, 0.8750, 1.0000]
    ## red   = [0.2082, 0.0592, 0.0780, 0.0232, 0.1802, 0.5301, 0.8186, 0.9956, 0.9764]
    ## green = [0.1664, 0.3599, 0.5041, 0.6419, 0.7178, 0.7492, 0.7328, 0.7862, 0.9832]
    ## blue  = [0.5293, 0.8684, 0.8385, 0.7914, 0.6425, 0.4662, 0.3499, 0.1968, 0.0539]

    
    ## stops = [0.00, 0.34, 0.61, 0.84, 1.00]
    ## red   = [0.00, 0.00, 0.87, 1.00, 0.51]
    ## green = [0.00, 0.81, 1.00, 0.20, 0.00]
    ## blue  = [0.51, 1.00, 0.12, 0.00, 0.00]
    
    ## s = array.array('d', stops)
    ## r = array.array('d', red)
    ## g = array.array('d', green)
    ## b = array.array('d', blue)

    ## npoints = len(s)
    ## ROOT.TColor.CreateGradientColorTable(npoints, s, r, g, b, 255)
    ## ROOT.gStyle.SetNumberContours(255)

    outputExists = False
    if glob.glob(options.odir+'/Ratios_1000pb_weighted.root'):
        outputExists = True
        
    main(options,args,outputExists)
        
##----##----##----##----##----##----##





import FWCore.ParameterSet.Config as cms
import FWCore.Utilities.FileUtils as FileUtils
from PhysicsTools.PatAlgos.patTemplate_cfg import *
import os 

relBase = os.environ['CMSSW_BASE']

process = cms.Process("AOD2NanoAOD")
process.load("Configuration.Geometry.GeometryIdeal_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
#process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.threshold = "WARNING"
process.MessageLogger.categories.append("AOD2NanoAOD")
process.MessageLogger.cerr.INFO = cms.untracked.PSet(
    limit=cms.untracked.int32(-1))
process.options = cms.untracked.PSet(wantSummary=cms.untracked.bool(True))

# Set the maximum number of events to be processed (-1 processes all events)
process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(-1))

##### ------ This set of file setup is for LOTS of files, not a short test ------
# Define files of dataset
#files = FileUtils.loadListFromFile("data/CMS_MonteCarlo2012_Summer12_DR53X_TTbar_8TeV-Madspin_aMCatNLO-herwig_AODSIM_PU_S10_START53_V19-v2_00000_file_index.txt")
#files.extend(FileUtils.loadListFromFile("data/CMS_MonteCarlo2012_Summer12_DR53X_TTbar_8TeV-Madspin_aMCatNLO-herwig_AODSIM_PU_S10_START53_V19-v2_20000_file_index.txt"))

#process.source = cms.Source(
#   "PoolSource", fileNames=cms.untracked.vstring(*files))

##### ------- This is a test file
process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring('root://eospublic.cern.ch//eos/opendata/cms/MonteCarlo2012/Summer12_DR53X/TTbar_8TeV-Madspin_aMCatNLO-herwig/AODSIM/PU_S10_START53_V19-v2/00000/000A9D3F-CE4C-E311-84F8-001E673969D2.root'))
#        fileNames = cms.untracked.vstring('root://eospublic.cern.ch//eos/opendata/cms/MonteCarlo2012/Summer12_DR53X/DY2JetsToLL_M-50_TuneZ2Star_8TeV-madgraph/AODSIM/PU_RD1_START53_V7N-v1/00000/000EFD4D-E1D0-E311-885A-0017A4770430.root'))
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(20))

# Set global tag
# We don't have set the global tag for the educational samples. This simplifies running the code since we don't have to access the database.
process.load('Configuration.StandardSequences.Services_cff')
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.globaltag = "START53_V27::All"

# Load PAT config                                                                                                                     
process.load("RecoTauTag.Configuration.RecoPFTauTag_cff") # re-run tau discriminators (new version)                               
process.load("PhysicsTools.PatAlgos.patSequences_cff")
process.load('Configuration.StandardSequences.Reconstruction_cff')
process.load('RecoJets.Configuration.RecoPFJets_cff')
process.load('RecoJets.Configuration.RecoJets_cff')
process.load('RecoJets.JetProducers.TrackJetParameters_cfi')
process.load('JetMETCorrections.Configuration.DefaultJEC_cff')

# Configure PAT to use PF2PAT instead of AOD sources                                                                                 
# this function will modify the PAT sequences.                                                                                              
from PhysicsTools.PatAlgos.tools.pfTools import *
from PhysicsTools.PatAlgos.tools.coreTools import *
from PhysicsTools.PatAlgos.tools.metTools import *
from PhysicsTools.PatAlgos.tools.jetTools import *
from PhysicsTools.PatAlgos.tools.coreTools import *
from PhysicsTools.SelectorUtils.pvSelector_cfi import pvSelector

process.goodOfflinePrimaryVertices = cms.EDFilter(
    "VertexSelector",
    filter = cms.bool(False),
    src = cms.InputTag("offlinePrimaryVertices"),
    cut = cms.string("!isFake && ndof > 4 && abs(z) <= 24 && position.rho < 2")
    )

process.ak5PFJets.doAreaFastjet = True
addPfMET(process, 'PF')

addJetCollection(process,cms.InputTag('ak5PFJets'),
                 'AK5', 'PFCorr',
                 doJTA        = True,
                 doBTagging   = True,
                 jetCorrLabel = ('AK5PF', cms.vstring(['L1FastJet','L2Relative','L3Absolute'])),#'L2L3Residual'])),          
                 doType1MET   = True,
                 doL1Cleaning = True,
                 doL1Counters = False,
                 doJetID      = True,
                 jetIdLabel   = "ak5",
                 #outputModules= ['out']                                                                                   
                 )

from RecoMET.METFilters.trackingFailureFilter_cfi import trackingFailureFilter
process.trackingFailureFilter = trackingFailureFilter.clone()
process.trackingFailureFilter.VertexSource = cms.InputTag('goodOfflinePrimaryVertices')

# Number of events to be skipped (0 by default)
process.source.skipEvents = cms.untracked.uint32(0)

# Output Module Configuration (expects a path 'p')
#process.out = cms.OutputModule("PoolOutputModule",
#        fileName = cms.untracked.string('jet_corr_name.root'),
        #SelectEvents = cms.untracked.PSet( SelectEvents = cms.vstring('p') ),
#        outputCommands = cms.untracked.vstring('keep *')
#        )

# Register fileservice for output file
process.aod2nanoaod = cms.EDAnalyzer("AOD2NanoAOD", 
        jecL1Name = cms.FileInPath('workspace/AOD2NanoAODOutreachTool/JEC_MC/START53_V27_L1FastJet_AK5PF.txt'),
        jecL2Name = cms.FileInPath('workspace/AOD2NanoAODOutreachTool/JEC_MC/START53_V27_L2Relative_AK5PF.txt'),
        jecL3Name = cms.FileInPath('workspace/AOD2NanoAODOutreachTool/JEC_MC/START53_V27_L3Absolute_AK5PF.txt'),
        jecUncName = cms.FileInPath('workspace/AOD2NanoAODOutreachTool/JEC_MC/START53_V27_Uncertainty_AK5PF.txt'),
        isData = cms.bool(False)
        )

process.TFileService = cms.Service(
    "TFileService", fileName=cms.string("output.root"))

process.p = cms.Path(process.patDefaultSequence * process.aod2nanoaod)
#process.ep = cms.EndPath(process.out)


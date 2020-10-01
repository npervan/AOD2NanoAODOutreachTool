import FWCore.ParameterSet.Config as cms
import FWCore.Utilities.FileUtils as FileUtils
import FWCore.PythonUtilities.LumiList as LumiList
import FWCore.ParameterSet.Types as CfgTypes
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

##### ------ This set of file setup is for LOTS of files, not a short test ------
# Define files of dataset
#files = FileUtils.loadListFromFile("data/CMS_Run2012B_DoubleMuParked_AOD_22Jan2013-v1_10000_file_index.txt")
#files.extend(FileUtils.loadListFromFile("data/CMS_Run2012B_DoubleMuParked_AOD_22Jan2013-v1_20000_file_index.txt"))
#files.extend(FileUtils.loadListFromFile("data/CMS_Run2012B_DoubleMuParked_AOD_22Jan2013-v1_20001_file_index.txt"))
#files.extend(FileUtils.loadListFromFile("data/CMS_Run2012B_DoubleMuParked_AOD_22Jan2013-v1_20002_file_index.txt"))
#files.extend(FileUtils.loadListFromFile("data/CMS_Run2012B_DoubleMuParked_AOD_22Jan2013-v1_210000_file_index.txt"))
#files.extend(FileUtils.loadListFromFile("data/CMS_Run2012B_DoubleMuParked_AOD_22Jan2013-v1_30000_file_index.txt"))
#files.extend(FileUtils.loadListFromFile("data/CMS_Run2012B_DoubleMuParked_AOD_22Jan2013-v1_310000_file_index.txt"))

#process.source = cms.Source(
#   "PoolSource", fileNames=cms.untracked.vstring(*files))

##### ------- This is a test file
process.source = cms.Source("PoolSource",
        fileNames = cms.untracked.vstring('root://eospublic.cern.ch//eos/opendata/cms/Run2012B/DoubleMuParked/AOD/22Jan2013-v1/10000/1EC938EF-ABEC-E211-94E0-90E6BA442F24.root'))

# Set the maximum number of events to be processed (-1 processes all events)
process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(-1))

# Set global tag
# We don't have set the global tag for the educational samples. This simplifies running the code since we don't have to access the database.
process.load('Configuration.StandardSequences.Services_cff')
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.globaltag = "FT_R_53_V18::All"

# Apply JSON file with lumi mask (needs to be done after the process.source definition)
goodJSON = "data/Cert_190456-208686_8TeV_22Jan2013ReReco_Collisions12_JSON.txt"
myLumis = LumiList.LumiList(filename=goodJSON).getCMSSWString().split(",")
process.source.lumisToProcess = CfgTypes.untracked(
    CfgTypes.VLuminosityBlockRange())
process.source.lumisToProcess.extend(myLumis)

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
removeMCMatchingPF2PAT( process )
runOnData(process)
addPfMET(process, 'PF')

addJetCollection(process,cms.InputTag('ak5PFJets'),
                 'AK5', 'PFCorr',
                 doJTA        = True,
                 doBTagging   = True,
                 jetCorrLabel = ('AK5PF', cms.vstring(['L1FastJet','L2Relative','L3Absolute','L2L3Residual'])),          
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

# Register fileservice for output file
process.aod2nanoaod = cms.EDAnalyzer("AOD2NanoAOD", 
        jecL1Name = cms.FileInPath('workspace/AOD2NanoAODOutreachTool/JEC_DATA/FT53_V21A_AN6_L1FastJet_AK5PF.txt'),
        jecL2Name = cms.FileInPath('workspace/AOD2NanoAODOutreachTool/JEC_DATA/FT53_V21A_AN6_L2Relative_AK5PF.txt'),
        jecL3Name = cms.FileInPath('workspace/AOD2NanoAODOutreachTool/JEC_DATA/FT53_V21A_AN6_L3Absolute_AK5PF.txt'),
        jecL2L3Name = cms.FileInPath('workspace/AOD2NanoAODOutreachTool/JEC_DATA/FT53_V21A_AN6_L2L3Residual_AK5PF.txt'),
        jecUncName = cms.FileInPath('workspace/AOD2NanoAODOutreachTool/JEC_DATA/FT53_V21A_AN6_Uncertainty_AK5PF.txt'),
        isData = cms.bool(True)
)

process.TFileService = cms.Service(
    "TFileService", fileName=cms.string("output.root"))

process.p = cms.Path(process.patDefaultSequence * process.aod2nanoaod)

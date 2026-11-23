package LegacyModel {
  private import PysspCore::*;

  attribute def LegacySsp :> SspMetadata {
    attribute source = "models/ssp/example/ssp";
  }

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
    attribute stepSize = 0.001;
  }

  part def LegacyBody :> SspModel {
    attribute ssp_meta : LegacySsp;
  }

  part def baseline :> Analysis {
    attribute experiment_baseline : BaselineExperiment;
    part sut : LegacyBody;
  }
}

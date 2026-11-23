package LegacyAnalysis {
  private import PysspCore::*;

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
    attribute stepSize = 0.001;
  }

  part def LegacyModel :> SspModel;

  part def baseline :> Analysis {
    attribute experiment_baseline : BaselineExperiment;
    part sut : LegacyModel;
  }
}

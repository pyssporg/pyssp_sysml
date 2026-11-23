package ModelOwnedAnalysis {
  private import PysspCore::*;

  port def LeafParameters :> ParameterInterface {
    attribute k : Real;
  }

  attribute def ScenarioSet :> ParameterSet {
    attribute k = 2.0;
  }

  attribute def BaselineExperiment :> Experiment {
    attribute startTime = 0.0;
    attribute stopTime = 1.0;
    attribute stepSize = 0.1;
  }

  part def Leaf {
    in port parameters : LeafParameters;
  }

  part def System :> SspModel {
    attribute scenario : ScenarioSet;
    part leaf : Leaf;
    bind leaf.parameters.k = scenario.k;
  }

  part def baseline :> Analysis {
    attribute experiment_baseline : BaselineExperiment;
    part sut : System;
  }
}

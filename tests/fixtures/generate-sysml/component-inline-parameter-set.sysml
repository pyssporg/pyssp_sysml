package RecoveredFromSSD {
  private import PysspCore::*;

  port def GainParameters :> ParameterInterface {
    attribute k : Real;
  }

  attribute def parameters :> ParameterSet {
    attribute k : Real = 4.0;
  }

  part def Gain {
    in port parameters : GainParameters;
  }

  part def ParamDemo {
    attribute parameters_set : parameters;
    part gain : Gain;
    bind gain.parameters = parameters_set;
  }
}

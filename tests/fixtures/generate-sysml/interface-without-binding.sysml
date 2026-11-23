package RecoveredFromSSD {
  private import PysspCore::*;

  port def GainParameters :> ParameterInterface {
    attribute k : Real;
  }

  part def Gain {
    in port parameters : GainParameters;
  }

  part def ParamDemo {
    part gain : Gain;
  }
}

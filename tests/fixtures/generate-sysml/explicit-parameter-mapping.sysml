package RecoveredFromSSD {
  private import PysspCore::*;

  port def CompParameters :> ParameterInterface {
    attribute count : Integer;
    attribute xs : Real[2];
  }

  attribute def Nom :> ParameterSet {
    attribute n : Integer = 5;
    attribute x : Real[2] = (1.0, 2.0);
  }

  part def Comp {
    in port parameters : CompParameters;
  }

  part def ParamDemo {
    attribute Nom : Nom;
    part comp : Comp;
    bind comp.parameters.count = Nom.n;
    bind comp.parameters.xs = Nom.x;
  }
}

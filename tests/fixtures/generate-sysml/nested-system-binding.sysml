package RecoveredFromSSD {
  private import PysspCore::*;

  port def InnerParameters :> ParameterInterface {
    attribute k : Real;
  }

  attribute def Nom :> ParameterSet {
    attribute k : Real = 3.0;
  }

  part def Demo {
    attribute Nom : Nom;
    part outer : outer;
    bind outer.inner.parameters = Nom;
  }

  part def Inner {
    in port parameters : InnerParameters;
  }

  part def outer {
    part inner : Inner;
  }
}

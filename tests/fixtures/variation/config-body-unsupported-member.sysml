package ConfigBodyUnsupportedMember {
  part def SspModel;
  port def RealSignal {
    attribute value : Real;
  }
  part def Gain {
    in port u : RealSignal;
    out port y : RealSignal;
  }

  part def System :> SspModel {
    part sub : Gain {
      port p : RealSignal;
    }
  }
}

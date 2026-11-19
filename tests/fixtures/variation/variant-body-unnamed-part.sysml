package VariantBodyUnnamedPart {
  part def SspModel;
  port def RealSignal {
    attribute value : Real;
  }
  part def Gain {
    in port u : RealSignal;
    out port y : RealSignal;
  }

  variation part def PathChoice {
    variant part directPath {
      part : Gain;
    }
  }

  part def System :> SspModel {
    part path : PathChoice;
  }
}

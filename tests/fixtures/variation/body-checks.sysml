package BodyChecks {
  part def SspModel;

  port def RealSignal {
    attribute value : Real;
  }

  part def Gain {
    in port u : RealSignal;
    out port y : RealSignal;
  }

  variation part def GhostChoice {
    in port u : RealSignal;
    out port y : RealSignal;

    variant part directPath {
      part gain : Gain;
      connect u to gain.u;
      connect gain.y to ghost.y;
    }
  }

  part def GhostSystem :> SspModel {
    part path : GhostChoice;
  }

  part def Collision__directPath;

  variation part def Collision {
    in port u : RealSignal;

    variant part directPath {
      part gain : Gain;
      connect u to gain.u;
    }
  }

  part def CollisionSystem :> SspModel {
    part path : Collision;
  }

  variation part def AttributeChoice {
    variant part withValues {
      part gain : Gain;
      attribute shadowedValue : Real;
    }
  }

  part def AttributeSystem :> SspModel {
    attribute shadowedValue : Real = 0.0;
    part path : AttributeChoice;
  }
}

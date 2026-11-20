package Validate {
  port def ParameterInterface;
  attribute def ParameterSet;

  part def FmuModel;

  port def CompParameters :> ParameterInterface {
    attribute waypointX_km : Real[2];
  }

  attribute def NominalSet :> ParameterSet {
    attribute waypointX_km = (1.0, 2.0);
  }

  attribute def FmuMetadata {
    attribute source : String;
    attribute implementation : String;
  }

  attribute def CompFmu :> FmuMetadata {
    attribute source = "Comp.fmu";
    attribute implementation = "CoSimulation";
  }

  part def Comp :> FmuModel {
    attribute fmu_meta : CompFmu;
    in port parameters : CompParameters;
  }

  part def SystemComposition {
    attribute nominal : NominalSet;
    part comp : Comp;
    bind comp.parameters.waypointX_km = nominal.waypointX_km;
  }
}

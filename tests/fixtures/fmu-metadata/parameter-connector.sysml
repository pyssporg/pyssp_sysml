package Example {
          private import PysspCore::*;

          attribute def CompFmu :> FmuMetadata {
            attribute implementation = "CoSimulation";
          }

          port def CompParameters :> ParameterInterface {
            attribute gain : Real;
          }

          part def Comp :> FmuModel {
            attribute fmu_meta : CompFmu;
            in port parameters : CompParameters;
          }

          part def $COMPOSITION_NAME {
            part comp : Comp;
          }
        }

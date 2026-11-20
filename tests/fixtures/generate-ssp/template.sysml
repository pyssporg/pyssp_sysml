package Example {
          $parameter_defs

          part def FmuModel;

          attribute def FmuMetadata {
            attribute source : String;
            attribute implementation : String;
          }

          attribute def CompFmu :> FmuMetadata {
            $metadata_fields
          }

          port def Signal {
            attribute y : Real;
          }

          part def Comp :> FmuModel {
            attribute fmu_meta : CompFmu;
            $parameter_port
            out port output : Signal;
          }

          part def $COMPOSITION_NAME {
            part comp : Comp;
            $composition_parameters
          }
        }

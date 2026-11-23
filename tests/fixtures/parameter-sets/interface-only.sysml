    package Example {
      private import PysspCore::*;
      port def AutopilotParameters :> ParameterInterface {
        attribute waypointCount : Integer;
        attribute waypointX_km : Real[3];
      }
      part def AutopilotModule {
        in port parameters : AutopilotParameters;
      }
      part def $COMPOSITION_NAME {
        part autopilot : AutopilotModule;
      }
    }

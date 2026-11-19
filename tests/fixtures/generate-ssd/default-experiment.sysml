package Example {
          attribute def ExperimentDefaults :> DefaultExperiment {
            attribute startTime = 2.0;
            attribute stopTime = 8.0;
          }

          port def Signal {
            attribute x : Real;
          }

          part def Source {
            out port outSig : Signal;
          }

          part def $COMPOSITION_NAME {
            attribute defaults : ExperimentDefaults;
            part src : Source;
          }
        }

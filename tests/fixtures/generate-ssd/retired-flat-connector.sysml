package Example {
          port def Signal {
            attribute pyssp_flat_connector : Boolean = true;
            attribute x : Real;
          }

          part def Source {
            out port outSig : Signal;
          }

          part def Model {
            part src : Source;
          }
        }

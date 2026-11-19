package Directions {
          port def Signal { attribute level : Real; }

          port def MixedSignal {
            in attribute p[3] : Real;
            out attribute m : Real;
            attribute u : Real;
          }

          part def Directions {
            in port a : Signal;
            out port b : Signal;
            inout port c : Signal;
            port plain : Signal;
          }
        }

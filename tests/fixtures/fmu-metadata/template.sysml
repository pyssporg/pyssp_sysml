package Example {
      part def FmuModel;

      $marker

      $concrete

      part def Comp :> FmuModel {
        $part_body
      }

      part def $COMPOSITION_NAME {
        part comp : Comp;
      }
    }

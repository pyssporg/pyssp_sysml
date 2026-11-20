package ArrayAttributeMismatch {
  port def Signal2 {
    attribute p[2] : Real;
  }

  port def Signal3 {
    attribute p[3] : Real;
  }

  part def Source {
    out port sig : Signal2;
  }

  part def Sink {
    in port sigIn : Signal3;
  }

  part def System {
    part source : Source;
    part sink : Sink;
    connect source.sig to sink.sigIn;
  }
}

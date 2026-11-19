package ArrayAttribute {
  port def Signal {
    attribute p[3] : Real;
  }

  part def Source {
    out port sig : Signal;
  }

  part def Sink {
    in port sigIn : Signal;
  }

  part def System {
    part source : Source;
    part sink : Sink;
    connect source.sig to sink.sigIn;
  }
}

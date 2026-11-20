package ScalarPorts {
  port def RealSignal {
    attribute value : Real;
  }

  part def Source {
    out port Alt : RealSignal;
  }

  part def Sink {
    in port AltIn : RealSignal;
  }

  part def System {
    part source : Source;
    part sink : Sink;

    connect source.Alt to sink.AltIn;
  }
}

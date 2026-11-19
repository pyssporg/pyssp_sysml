package InheritanceSsd {
  port def Signal {
    attribute value : Real;
  }

  port def ExtraSignal :> Signal {
    attribute flag : Integer;
  }

  part def Sink {
    in port u : Signal;
  }

  part def ExtraSink {
    in port u : ExtraSignal;
  }

  part def BaseLink {
    in port u : Signal;
    out port y : Signal;
    part sink : Sink;
    connect u to sink.u;
  }

  part def DerivedLink :> BaseLink {
    out port extra : ExtraSignal;
    part probe : ExtraSink;
    connect probe.u to extra;
  }

  part def System {
    part link : DerivedLink;
  }
}

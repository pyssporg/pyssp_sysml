package MirroredPorts {
  port def FeedOut {
    out attribute p : Real;
    in attribute m : Real;
  }

  port def FeedIn {
    in attribute p : Real;
    out attribute m : Real;
  }

  part def Source {
    out port feed : FeedOut;
  }

  part def Sink {
    in port feed : FeedIn;
  }

  part def System {
    part source : Source;
    part sink : Sink;

    connect source.feed to sink.feed;
  }
}

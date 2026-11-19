package ConjugatedPorts {
  port def Feed {
    out attribute p : Real;
    in attribute m : Real;
  }

  part def Source {
    out port feed : Feed;
  }

  part def Sink {
    in port feed : ~Feed;
  }

  part def System {
    part source : Source;
    part sink : Sink;

    connect source.feed to sink.feed;
  }
}

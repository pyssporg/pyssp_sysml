package BoundaryArray {
  port def Signal {
    attribute p[3] : Real;
  }

  part def Inner {
    in port u : Signal;
  }

  part def System {
    in port u : Signal;
    part inner : Inner;
    connect u to inner.u;
  }
}

package MemberDirections {
  port def MixedSignal {
    in attribute p[3] : Real;
    out attribute m : Real;
  }

  port def UnmarkedSignal {
    attribute n : Real;
  }

  part def Widget {
    inout port sig : MixedSignal;
    inout port fallback : UnmarkedSignal;
  }

  part def SystemComposition {
    part widget : Widget;
  }
}

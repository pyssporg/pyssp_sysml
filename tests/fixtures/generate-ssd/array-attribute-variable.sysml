package VariableArrayAttribute {
  port def Signal {
    attribute p[0..*] : Real;
  }

  part def Source {
    out port sig : Signal;
  }

  part def System {
    part source : Source;
  }
}

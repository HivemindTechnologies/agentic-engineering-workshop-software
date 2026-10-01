scalaVersion := "3.3.4"

name := "check-redundancies-cpd"

// PMD's copy/paste detector (CPD), pinned. Only the core and the Scala language module:
// CPD tokenizes Scala with the same scalameta lexer PMD ships, no rules and no CLI.
val pmdVersion = "7.28.0"

libraryDependencies ++= Seq(
  "net.sourceforge.pmd" % "pmd-core"          % pmdVersion,
  "net.sourceforge.pmd" % "pmd-scala_2.13"    % pmdVersion,
  // PMD logs through slf4j; without a binding it prints a warning on every run.
  "org.slf4j"           % "slf4j-nop"         % "1.7.36"
)

import net.sourceforge.pmd.cpd.{CPDConfiguration, CPDReport, CpdAnalysis, Match}
import net.sourceforge.pmd.lang.LanguageRegistry

import java.nio.charset.StandardCharsets
import java.nio.file.{FileSystems, Files, Path, Paths}
import scala.jdk.CollectionConverters.*

/** Copy/paste (redundancy) gate on PMD's CPD. JVM only: pmd-core plus the Scala language module. */
object CheckRedundancies:
  private val PmdVersion = "7.28.0"
  private val DefaultMinTokens = 50
  private val SnippetLines = 12
  private val QuietTop = 10

  private enum Verbosity:
    case Quiet, Normal, Verbose

  private final case class Options(
      root: Path,
      minTokens: Int,
      verbosity: Verbosity,
      report: Path,
      failOnFindings: Boolean,
      allow: List[String]
  )

  private final case class Location(file: String, start: Int, end: Int)
  private final case class Finding(tokens: Int, lines: Int, locations: List[Location], snippet: List[String]):
    def occurrences: Int = locations.size
    def impact: Int = lines * occurrences

  def main(args: Array[String]): Unit =
    parse(args.toList) match
      case Left(message) =>
        System.err.println(s"check-redundancies: $message")
        sys.exit(2)
      case Right(options) => sys.exit(run(options))

  private def parse(args: List[String]): Either[String, Options] =
    def loop(rest: List[String], acc: Options): Either[String, Options] = rest match
      case Nil => Right(acc)
      case "--min-tokens" :: v :: tail =>
        v.toIntOption.filter(_ > 0).toRight(s"bad --min-tokens: $v").flatMap(n => loop(tail, acc.copy(minTokens = n)))
      case "--verbosity" :: v :: tail =>
        v match
          case "quiet"   => loop(tail, acc.copy(verbosity = Verbosity.Quiet))
          case "normal"  => loop(tail, acc.copy(verbosity = Verbosity.Normal))
          case "verbose" => loop(tail, acc.copy(verbosity = Verbosity.Verbose))
          case other     => Left(s"bad --verbosity: $other (quiet|normal|verbose)")
      case "--report" :: v :: tail => loop(tail, acc.copy(report = Paths.get(v)))
      case "--allow" :: v :: tail => loop(tail, acc.copy(allow = acc.allow :+ v))
      case "--fail-on-findings" :: tail => loop(tail, acc.copy(failOnFindings = true))
      case flag :: _ if flag.startsWith("--") => Left(s"unknown flag: $flag")
      case root :: tail => loop(tail, acc.copy(root = Paths.get(root)))
    loop(
      args,
      Options(Paths.get("src"), DefaultMinTokens, Verbosity.Quiet, Paths.get("redundancy-report.json"), false, Nil)
    )

  private def run(o: Options): Int =
    val root = o.root.toAbsolutePath.normalize
    if !Files.isDirectory(root) then
      System.err.println(s"check-redundancies: not a directory: $root")
      2
    else
      val findings = analyse(root, sourceFiles(root, o.allow), o)
      val ranked = findings.sortBy(f => (-f.impact, -f.lines, -f.occurrences, f.locations.head.file))
      writeReport(o, ranked)
      println(s"findings: ${ranked.size}")
      if o.verbosity != Verbosity.Quiet then
        ranked.take(8).foreach { f =>
          val first = f.locations.head
          println(s"  ${f.lines} lines x${f.occurrences}: ${first.file}:${first.start}")
        }
      if o.failOnFindings && ranked.nonEmpty then 1 else 0

  private def sourceFiles(root: Path, allow: List[String]): List[Path] =
    val matchers = allow.map(g => FileSystems.getDefault.getPathMatcher(s"glob:$g"))
    val stream = Files.walk(root)
    try
      stream.iterator.asScala
        .filter(p => Files.isRegularFile(p) && p.getFileName.toString.endsWith(".scala"))
        .filterNot(p => root.relativize(p).iterator.asScala.exists(_.toString == "target"))
        .filterNot(p => matchers.exists(m => m.matches(root.relativize(p)) || m.matches(p)))
        .toList
        .sorted
    finally stream.close()

  private def analyse(root: Path, files: List[Path], o: Options): List[Finding] =
    val config = new CPDConfiguration(LanguageRegistry.CPD)
    config.setOnlyRecognizeLanguage(LanguageRegistry.CPD.getLanguageById("scala"))
    config.setMinimumTileSize(o.minTokens)
    config.setSourceEncoding(StandardCharsets.UTF_8)
    val analysis = CpdAnalysis.create(config)
    try
      files.foreach(f => analysis.files().addFile(f))
      var found = List.empty[Finding]
      analysis.performAnalysis((report: CPDReport) =>
        val errors = report.getProcessingErrors.asScala.toList
        if errors.nonEmpty then
          errors.foreach(e => System.err.println(s"check-redundancies: ${e.getFileId.getOriginalPath}: ${e.getMsg}"))
          sys.exit(2)
        found = report.getMatches.asScala.toList.map(toFinding(root, report, _))
      )
      found
    finally analysis.close()

  private def toFinding(root: Path, report: CPDReport, m: Match): Finding =
    val locations = m.iterator.asScala.toList.map { mark =>
      val loc = mark.getLocation
      Location(root.relativize(Paths.get(loc.getFileId.getAbsolutePath)).toString, loc.getStartLine, loc.getEndLine)
    }.sortBy(l => (l.file, l.start))
    val snippet = report.getSourceCodeSlice(m.getFirstMark).toString.linesIterator.take(SnippetLines).toList
    Finding(m.getTokenCount, m.getLineCount, locations, snippet)

  private def writeReport(o: Options, findings: List[Finding]): Unit =
    val shown = o.verbosity match
      case Verbosity.Quiet => findings.take(QuietTop).map(json(_, withSnippet = false))
      case Verbosity.Normal => findings.map(json(_, withSnippet = false))
      case Verbosity.Verbose => findings.map(json(_, withSnippet = true))
    val body = List(
      s"""  "tool": "pmd-cpd"""",
      s"""  "version": "$PmdVersion"""",
      s"""  "root": ${quote(o.root.toString)}""",
      s"""  "minimum_tokens": ${o.minTokens}""",
      s"""  "finding_count": ${findings.size}""",
      s"""  "findings": [${if shown.isEmpty then "" else shown.mkString("\n", ",\n", "\n  ")}]"""
    ).mkString("{\n", ",\n", "\n}\n")
    Option(o.report.toAbsolutePath.getParent).foreach(Files.createDirectories(_))
    Files.writeString(o.report, body, StandardCharsets.UTF_8)

  private def json(f: Finding, withSnippet: Boolean): String =
    val locations = f.locations
      .map(l => s"""{"file": ${quote(l.file)}, "start": ${l.start}, "end": ${l.end}}""")
      .mkString("[", ", ", "]")
    val snippet = if withSnippet then s""", "snippet": ${f.snippet.map(quote).mkString("[", ", ", "]")}""" else ""
    s"""    {"tokens": ${f.tokens}, "lines": ${f.lines}, "occurrences": ${f.occurrences}, "locations": $locations$snippet}"""

  private def quote(s: String): String =
    val escaped = s.flatMap {
      case '"'  => "\\\""
      case '\\' => "\\\\"
      case '\n' => "\\n"
      case '\r' => "\\r"
      case '\t' => "\\t"
      case c    => c.toString
    }
    s""""$escaped""""

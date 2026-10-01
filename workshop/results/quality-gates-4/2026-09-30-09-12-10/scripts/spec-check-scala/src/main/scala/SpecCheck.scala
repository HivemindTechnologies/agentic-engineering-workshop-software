import java.nio.charset.StandardCharsets
import java.nio.file.{FileSystems, Files, Path, Paths}
import java.util.regex.Pattern
import scala.jdk.CollectionConverters.*

object SpecCheck:
  private val Heading: Pattern = Pattern.compile(
    """^## M[0-9]+([A-Za-z][A-Za-z0-9_-]*)?: .+ \(Status: (PENDING|IMPLEMENTING|IMPLEMENTED|PARTIALLY_DONE|SKIPPED|POSTPONED|✅ DONE)\)$"""
  )
  private val Ac = "**Acceptance Criteria:**"
  private val Details = "**Implementation Details:**"
  private val Forbidden: Pattern = Pattern.compile("""^### (Implementation Details\b|M)""")
  private val Checkbox: Pattern = Pattern.compile("""^- \[[ x]\] .+$""")
  private val CheckedStatus = Set("(Status: IMPLEMENTED)", "(Status: ✅ DONE)")
  private val SpecName = FileSystems.getDefault.getPathMatcher("glob:SPEC.*.md")

  def main(args: Array[String]): Unit =
    if args.length != 1 then sys.exit(1)
    val raw = args(0)
    val path = Paths.get(raw)
    if !Files.exists(path) then
      System.err.println(s"$raw:1")
      sys.exit(1)
    if Files.isRegularFile(path) then
      checkFile(raw, path) match
        case Some(report) =>
          System.err.println(report)
          sys.exit(1)
        case None =>
          sys.exit(0)
    if Files.isDirectory(path) then
      val files =
        Files.list(path).iterator().asScala.filter(Files.isRegularFile(_)).toSeq.sortBy(_.getFileName.toString)
      if files.isEmpty then
        System.err.println(s"$raw:1")
        sys.exit(1)
      val reports = files.flatMap { child =>
        val display =
          if raw.endsWith("/") || raw.endsWith(java.io.File.separator) then raw + child.getFileName.toString
          else raw + java.io.File.separator + child.getFileName.toString
        checkFile(display, child)
      }
      if reports.nonEmpty then
        System.err.println(reports.mkString("\n"))
        sys.exit(1)
      sys.exit(0)
    System.err.println(s"$raw:1")
    sys.exit(1)

  private def nameOk(name: String): Boolean =
    SpecName.matches(Paths.get(name))

  private def checkFile(display: String, path: Path): Option[String] =
    if !nameOk(path.getFileName.toString) then return Some(s"$display:1")
    val text =
      try Files.readString(path, StandardCharsets.UTF_8)
      catch case _: Exception => return Some(s"$display:1")
    firstViolation(text.linesIterator.toSeq).map(line => s"$display:$line")

  private def firstViolation(lines: Seq[String]): Option[Int] =
    var index = 0
    while index < lines.length do
      val line = lines(index)
      if !line.startsWith("## M") then index += 1
      else
        var end = index + 1
        while end < lines.length && !lines(end).startsWith("## ") do end += 1
        val body = lines.slice(index + 1, end)
        val owns = body.contains(Ac) || body.exists(_.startsWith("**Acceptance"))
        if owns && !Heading.matcher(line).matches() then return Some(index + 1)
        var offset = 0
        while offset < body.length do
          val item = body(offset)
          val lineNo = index + 2 + offset
          if item.startsWith("**Acceptance") && item != Ac then return Some(lineNo)
          if Forbidden.matcher(item).lookingAt() then return Some(lineNo)
          offset += 1
        subsectionViolation(body, index + 2) match
          case Some(v) => return Some(v)
          case None =>
            if Heading.matcher(line).matches() && !body.contains(Ac) then return Some(index + 1)
            if Heading.matcher(line).matches() then
              boxViolation(line, body, index + 2) match
                case Some(v) => return Some(v)
                case None    => ()
        index = end
    None

  private def subsectionViolation(body: Seq[String], startLine: Int): Option[Int] =
    val criteria = scala.collection.mutable.ArrayBuffer.empty[Int]
    val details = scala.collection.mutable.ArrayBuffer.empty[Int]
    var offset = 0
    while offset < body.length do
      val item = body(offset)
      val lineNo = startLine + offset
      if item.startsWith(Details) && item != Details then return Some(lineNo)
      if item == Ac then criteria += lineNo
      else if item == Details then details += lineNo
      offset += 1
    if criteria.length > 1 then return Some(criteria(1))
    if details.length > 1 then return Some(details(1))
    if details.nonEmpty && (criteria.isEmpty || details(0) < criteria(0)) then return Some(details(0))
    None

  private def boxViolation(heading: String, body: Seq[String], startLine: Int): Option[Int] =
    val start = body.indexOf(Ac) + 1
    val end =
      body.indices
        .find(i => i >= start && body(i) == Details)
        .getOrElse(body.length)
    val status = heading.substring(heading.lastIndexOf("(Status: "))
    val partial = status == "(Status: PARTIALLY_DONE)"
    val checked = CheckedStatus.contains(status)
    var index = start
    while index < end do
      val item = body(index)
      if item != "" then
        if !Checkbox.matcher(item).matches() then return Some(startLine + index)
        if !partial && item.startsWith("- [x] ") != checked then return Some(startLine + index)
      index += 1
    None

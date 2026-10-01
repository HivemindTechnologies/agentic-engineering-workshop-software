//> using scala 3.3.4

/** ATX heading TOC for markdown files, with optional outline compare. */
import java.nio.charset.StandardCharsets
import java.nio.file.{Files, Path, Paths}
import scala.jdk.CollectionConverters.*
import scala.util.matching.Regex

val Heading: Regex = """^#{1,6} .*""".r

enum Mode:
  case List(showLines: Boolean, path: Path)
  case Compare(left: Path, right: Path)

enum DiffOp:
  case Keep(line: String)
  case Del(line: String)
  case Add(line: String)

def parse(raw: List[String]): Either[String, Mode] =
  val argv = raw.dropWhile(_ == "--")
  argv match
    case "--compare" :: a :: b :: Nil =>
      Right(Mode.Compare(Paths.get(a), Paths.get(b)))
    case "--compare" :: _ =>
      Left("usage: tocmd --compare <path-a> <path-b>")
    case rest =>
      var showLines = false
      var path: Option[String] = None
      var unknown: Option[String] = None
      rest.foreach {
        case "--lines" if path.isEmpty && unknown.isEmpty => showLines = true
        case flag if flag.startsWith("-") && path.isEmpty => unknown = Some(flag)
        case p if path.isEmpty && unknown.isEmpty         => path = Some(p)
        case other                                        => unknown = Some(other)
      }
      unknown match
        case Some(flag) => Left(s"unknown argument: $flag")
        case None =>
          path match
            case None    => Left("usage: tocmd [--lines] <path.md|directory>")
            case Some(p) => Right(Mode.List(showLines, Paths.get(p)))

def markdownPaths(path: Path): List[Path] =
  if !Files.exists(path) then Nil
  else if Files.isDirectory(path) then
    Files
      .list(path)
      .iterator()
      .asScala
      .filter(p => Files.isRegularFile(p) && p.getFileName.toString.endsWith(".md"))
      .toList
      .sortBy(_.getFileName.toString)
  else if Files.isRegularFile(path) then List(path)
  else Nil

def headingLines(path: Path, showLines: Boolean): List[String] =
  try
    val lines = Files.readAllLines(path, StandardCharsets.UTF_8).asScala.toList
    lines.zipWithIndex.collect {
      case (line, idx) if Heading.matches(line) =>
        if showLines then s"${idx + 1} $line" else line
    }
  catch case _: Exception =>
    sys.exit(1)

def outline(path: Path): List[String] =
  val targets = markdownPaths(path)
  if targets.isEmpty then Nil
  else
    val labelPaths = targets.size > 1
    val blocks = targets.map { target =>
      val headings = headingLines(target, showLines = false)
      if labelPaths then target.toString :: headings else headings
    }
    blocks.zipWithIndex.flatMap { (block, index) =>
      if index == 0 then block else "" :: block
    }

def writeToc(path: Path, showLines: Boolean, labelPath: Boolean): Unit =
  if labelPath then println(path)
  headingLines(path, showLines).foreach(println)

def lcsOps(a: List[String], b: List[String]): List[DiffOp] =
  val n = a.length
  val m = b.length
  val dp = Array.ofDim[Int](n + 1, m + 1)
  for i <- n - 1 to 0 by -1 do
    for j <- m - 1 to 0 by -1 do
      dp(i)(j) =
        if a(i) == b(j) then dp(i + 1)(j + 1) + 1
        else math.max(dp(i + 1)(j), dp(i)(j + 1))
  val out = scala.collection.mutable.ListBuffer.empty[DiffOp]
  var i = 0
  var j = 0
  while i < n || j < m do
    if i < n && j < m && a(i) == b(j) then
      out += DiffOp.Keep(a(i))
      i += 1
      j += 1
    else if j < m && (i == n || dp(i)(j + 1) >= dp(i + 1)(j)) then
      out += DiffOp.Add(b(j))
      j += 1
    else
      out += DiffOp.Del(a(i))
      i += 1
  out.toList

def printDiff(leftName: String, rightName: String, left: List[String], right: List[String]): Unit =
  println(s"--- $leftName")
  println(s"+++ $rightName")
  lcsOps(left, right).foreach {
    case DiffOp.Keep(line) => println(s"  $line")
    case DiffOp.Del(line)  => println(s"- $line")
    case DiffOp.Add(line)  => println(s"+ $line")
  }

@main def tocmd(args: String*): Unit =
  parse(args.toList) match
    case Left(msg) =>
      System.err.println(msg)
      sys.exit(1)
    case Right(Mode.List(showLines, path)) =>
      val targets = markdownPaths(path)
      if targets.isEmpty then sys.exit(1)
      val labelPaths = targets.size > 1
      targets.zipWithIndex.foreach { (target, index) =>
        if index > 0 then println()
        writeToc(target, showLines, labelPaths)
      }
    case Right(Mode.Compare(left, right)) =>
      if !Files.exists(left) || !Files.exists(right) then sys.exit(1)
      val leftLines = outline(left)
      val rightLines = outline(right)
      if leftLines.isEmpty && Files.isDirectory(left) then sys.exit(1)
      if rightLines.isEmpty && Files.isDirectory(right) then sys.exit(1)
      if leftLines == rightLines then sys.exit(0)
      printDiff(left.toString, right.toString, leftLines, rightLines)
      sys.exit(1)

package todo.core

/** A todo title: never blank, never whitespace-only. The only way to get one is [[Title.apply]]. */
opaque type Title = String

object Title:
  enum Error:
    case Blank

  /**
   * Smart constructor: fails on a blank or whitespace-only title instead of silently trimming it to
   * something else.
   */
  def apply(raw: String): Either[Error, Title] =
    if raw.trim.isEmpty then Left(Error.Blank) else Right(raw)

  extension (title: Title) def value: String = title

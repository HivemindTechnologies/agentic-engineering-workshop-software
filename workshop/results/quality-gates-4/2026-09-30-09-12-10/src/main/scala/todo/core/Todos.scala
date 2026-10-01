package todo.core

/** Pure operations over `List[Todo]`. No `IO` anywhere — the CLI layer wires these to the store. */
object Todos:
  enum Error:
    case InvalidTitle(reason: Title.Error)
    case UnknownId(id: Int)
    case InvalidField(message: String)

  final case class Meta(
      due: Option[String] = None,
      clearDue: Boolean = false,
      priority: Option[String] = None,
      clearPriority: Boolean = false,
      tags: Option[List[String]] = None,
      assignees: Option[List[String]] = None,
      assigner: Option[String] = None,
      clearAssigner: Boolean = false
  )

  def add(
      existing: List[Todo],
      rawTitle: String,
      meta: Meta = Meta(),
      defaultAssigner: Option[String] = None
  ): Either[Error, (Todo, List[Todo])] =
    for
      title <- Title(rawTitle).left.map(Error.InvalidTitle.apply)
      fields <- parseFields(meta, defaultAssigner, inherit = None)
    yield
      val created = Todo(
        nextId(existing),
        title,
        done = false,
        due = fields.due,
        priority = fields.priority,
        tags = fields.tags,
        assignees = fields.assignees,
        assigner = fields.assigner
      )
      (created, existing :+ created)

  def markDone(existing: List[Todo], id: Int): Either[Error, List[Todo]] =
    findIndex(existing, id).map { idx =>
      val todo = existing(idx)
      if todo.done then existing else existing.updated(idx, todo.copy(done = true))
    }

  def edit(
      existing: List[Todo],
      id: Int,
      rawTitle: Option[String] = None,
      meta: Meta = Meta(),
      defaultAssigner: Option[String] = None
  ): Either[Error, List[Todo]] =
    for
      idx <- findIndex(existing, id)
      title <- rawTitle match
        case None    => Right(existing(idx).title)
        case Some(t) => Title(t).left.map(Error.InvalidTitle.apply)
      fields <- parseFields(meta, defaultAssigner, inherit = Some(existing(idx)))
    yield existing.updated(
      idx,
      existing(idx).copy(
        title = title,
        due = fields.due,
        priority = fields.priority,
        tags = fields.tags,
        assignees = fields.assignees,
        assigner = fields.assigner
      )
    )

  def remove(existing: List[Todo], id: Int): Either[Error, List[Todo]] =
    findIndex(existing, id).map(idx => existing.patch(idx, Nil, 1))

  def filter(
      todos: List[Todo],
      tag: Option[String] = None,
      assignee: Option[String] = None,
      priority: Option[String] = None
  ): Either[Error, List[Todo]] =
    for p <- priority match
        case None    => Right(None)
        case Some(s) => Priority.parse(s).map(Some(_)).left.map(Error.InvalidField.apply)
    yield todos.filter { t =>
      tag.forall(tg => t.tags.exists(_.value == tg)) &&
      assignee.forall(a => t.assignees.exists(_.value == a)) &&
      p.forall(pr => t.priority.contains(pr))
    }

  final private case class Fields(
      due: Option[DueDate],
      priority: Option[Priority],
      tags: List[TodoTag],
      assignees: List[Email],
      assigner: Option[Email]
  )

  private def parseFields(
      meta: Meta,
      defaultAssigner: Option[String],
      inherit: Option[Todo]
  ): Either[Error, Fields] =
    for
      due <-
        if meta.clearDue then Right(None)
        else
          meta.due match
            case Some(s) => DueDate.parse(s).map(Some(_)).left.map(Error.InvalidField.apply)
            case None    => Right(inherit.flatMap(_.due))
      priority <-
        if meta.clearPriority then Right(None)
        else
          meta.priority match
            case Some(s) => Priority.parse(s).map(Some(_)).left.map(Error.InvalidField.apply)
            case None    => Right(inherit.flatMap(_.priority))
      tags <- meta.tags match
        case None      => Right(inherit.map(_.tags).getOrElse(Nil))
        case Some(Nil) => Right(Nil)
        case Some(xs)  => parseTags(xs)
      assignees <- meta.assignees match
        case None      => Right(inherit.map(_.assignees).getOrElse(Nil))
        case Some(Nil) => Right(Nil)
        case Some(xs)  => parseEmails(xs)
      assigner <-
        if meta.clearAssigner then Right(None)
        else
          meta.assigner match
            case Some(s) => Email(s).map(Some(_)).left.map(Error.InvalidField.apply)
            case None =>
              inherit.flatMap(_.assigner) match
                case some @ Some(_) => Right(some)
                case None =>
                  defaultAssigner match
                    case None    => Right(None)
                    case Some(s) => Email(s).map(Some(_)).left.map(Error.InvalidField.apply)
    yield Fields(due, priority, tags, assignees, assigner)

  private def parseTags(xs: List[String]): Either[Error, List[TodoTag]] =
    xs.foldLeft[Either[Error, List[TodoTag]]](Right(Nil)) { (acc, raw) =>
      for
        ts <- acc
        t <- TodoTag(raw).left.map(Error.InvalidField.apply)
      yield if ts.exists(_.value == t.value) then ts else ts :+ t
    }

  private def parseEmails(xs: List[String]): Either[Error, List[Email]] =
    xs.foldLeft[Either[Error, List[Email]]](Right(Nil)) { (acc, raw) =>
      for
        es <- acc
        e <- Email(raw).left.map(Error.InvalidField.apply)
      yield if es.exists(_.value == e.value) then es else es :+ e
    }

  private def findIndex(existing: List[Todo], id: Int): Either[Error, Int] =
    existing.indexWhere(_.id.value == id) match
      case -1  => Left(Error.UnknownId(id))
      case idx => Right(idx)

  private def nextId(existing: List[Todo]): TodoId =
    TodoId(existing.map(_.id.value).maxOption.getOrElse(0) + 1)

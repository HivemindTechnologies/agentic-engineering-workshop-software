object B:
  def two(x: Int): Int =
    // CPD-OFF
    val a = x + 1
    val b = a * 2
    val c = b - 3
    val d = c + 4
    val e = d * 5
    val f = e - 6
    val g = f + 7
    val h = g * 8
    f + h
    // CPD-ON

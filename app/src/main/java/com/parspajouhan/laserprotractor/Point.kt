package com.parspajouhan.laserprotractor

import kotlin.math.hypot
import kotlin.math.sqrt

data class Point(
    val x: Float,
    val y: Float
)

fun Point.margin(point: Point): Float {
    return sqrt(hypot((point.x - this.x), (point.y - this.y)))
}
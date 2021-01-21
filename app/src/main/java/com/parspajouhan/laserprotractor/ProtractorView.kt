package com.parspajouhan.laserprotractor

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.Path
import android.util.AttributeSet
import android.view.MotionEvent
import androidx.appcompat.widget.AppCompatImageView

class ProtractorView : AppCompatImageView {
    constructor(context: Context) : super(context)
    constructor(context: Context, attrs: AttributeSet?) : super(context, attrs)
    constructor(context: Context, attrs: AttributeSet?, defStyleAttr: Int) : super(
        context,
        attrs,
        defStyleAttr
    )

    private val margin = 10
    private var pointOne: Point? = null
    private var pointTwo: Point? = null
    private var pointThree: Point? = null
    private var paint: Paint = Paint().apply {
        color = Color.BLUE
        style = Paint.Style.STROKE
        strokeWidth = 8.0f
    }
    private var path: Path? = null

    fun setPoints(pointOne: Point, pointTwo: Point, pointThree: Point) {
        this.pointOne = pointOne
        this.pointTwo = pointTwo
        this.pointThree = pointThree
        makePath()
        invalidate()
    }

    private fun makePath() {
        path = Path()
        path!!.moveTo(pointOne!!.x, pointOne!!.y)
        path!!.lineTo(pointTwo!!.x, pointTwo!!.y)
        path!!.lineTo(pointThree!!.x, pointThree!!.y)
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        path?.let {
            canvas.drawPath(
                it,
                paint
            )
        }
    }

    override fun onTouchEvent(event: MotionEvent): Boolean {
        super.onTouchEvent(event)
        val touchPoint = Point(event.x, event.y)
        val touchMargin = minOf(
            pointOne!!.margin(touchPoint),
            pointTwo!!.margin(touchPoint),
            pointThree!!.margin(touchPoint)
        )

        when (event.action) {
            MotionEvent.ACTION_DOWN -> {
                if (touchMargin > margin)
                    return true
                when (touchMargin) {
                    pointOne!!.margin(touchPoint) -> pointOne = touchPoint
                    pointTwo!!.margin(touchPoint) -> pointTwo = touchPoint
                    pointThree!!.margin(touchPoint) -> pointThree = touchPoint
                }
            }
            MotionEvent.ACTION_MOVE -> {
                when (touchMargin) {
                    pointOne!!.margin(touchPoint) -> pointOne = touchPoint
                    pointTwo!!.margin(touchPoint) -> pointTwo = touchPoint
                    pointThree!!.margin(touchPoint) -> pointThree = touchPoint
                }
            }
            MotionEvent.ACTION_UP -> {
                return true
            }

        }
        makePath()
        invalidate()
        return true
    }
}
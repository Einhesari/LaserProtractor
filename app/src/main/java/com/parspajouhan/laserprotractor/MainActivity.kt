package com.parspajouhan.laserprotractor

import android.content.Intent
import android.graphics.BitmapFactory
import android.net.Uri
import android.os.Bundle
import android.util.Base64
import android.view.View
import android.widget.Button
import android.widget.LinearLayout
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.widget.addTextChangedListener
import com.chaquo.python.PyObject
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform
import com.google.android.material.textfield.TextInputEditText
import com.google.android.material.textfield.TextInputLayout
import java.io.ByteArrayOutputStream
import java.io.FileNotFoundException
import java.io.IOException
import java.io.InputStream
import kotlin.math.sin


class MainActivity : AppCompatActivity() {
    lateinit var python: Python
    private val selectImageRequestCode = 1000
    private lateinit var imageView: ProtractorView
    private lateinit var loading: LinearLayout
    private lateinit var container: LinearLayout
    private lateinit var edtN2: TextInputEditText
    private lateinit var edtY: TextInputEditText
    private lateinit var edtTheta1: TextInputEditText
    private lateinit var edtTheta2: TextInputEditText
    private lateinit var edtN1: TextInputEditText
    private lateinit var btnPhoto: Button
    private lateinit var pointOne: Point
    private lateinit var pointTwo: Point
    private lateinit var pointThree: Point
    private lateinit var pythonObj: PyObject
    private var theta2 = 0.0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        imageView = findViewById(R.id.imageview)
        container = findViewById(R.id.container)
        btnPhoto = findViewById(R.id.btn_photo)
        edtN1 = findViewById(R.id.edt_N1)
        edtTheta2 = findViewById(R.id.edt_theta2)
        edtTheta1 = findViewById(R.id.edt_theta1)
        loading = findViewById(R.id.loading)
        edtN2 = findViewById(R.id.edt_N2)
        edtY = findViewById(R.id.edt_Y)
        btnPhoto.setOnClickListener {
            val intent = Intent(Intent.ACTION_GET_CONTENT)
            intent.type = "image/*"
            startActivityForResult(intent, selectImageRequestCode)
        }
        if (!Python.isStarted())
            Python.start(AndroidPlatform(this))
        python = Python.getInstance()
        loading.visibility = View.VISIBLE
        container.visibility = View.GONE
        Thread {
            pythonObj = python.getModule("RAD")
            runOnUiThread {
                loading.visibility = View.GONE
                container.visibility = View.VISIBLE
            }
        }.start()
        edtTheta2.addTextChangedListener(afterTextChanged = {
            it?.toString()?.let { theta ->
                if (theta.isNotEmpty()) {
                    theta2 = theta.toDouble()
                    edtN2.setText(
                        calculateN2(
                            edtTheta1.text.toString().toDouble(),
                            edtN1.text.toString().toDouble()
                        ).toString()
                    )
                    edtY.setText(calculateY(edtN2.text.toString().toDouble()))
                }
            }
        })
        findViewById<TextInputLayout>(R.id.layout).setOnClickListener {
            Toast.makeText(this, "clicked", Toast.LENGTH_LONG).show()
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == selectImageRequestCode && resultCode == RESULT_OK && data != null) {
            try {
                loading.visibility = View.VISIBLE
                container.visibility = View.GONE
                Thread {
                    val imageUri: Uri? = data.data
                    val imageStream: InputStream? = contentResolver.openInputStream(imageUri!!)
                    val inputData: ByteArray = getBytes(imageStream!!)
                    val result = mutableListOf<String>()
                    try {
                        result.addAll(
                            pythonObj.callAttr(
                                "RAD",
                                Base64.encodeToString(inputData, Base64.DEFAULT)
                            ).toString().split(" ")
                        )

                    } catch (e: Exception) {
                        runOnUiThread {
                            loading.visibility = View.GONE
                            container.visibility = View.VISIBLE
                            Toast.makeText(this, "Error in processing image", Toast.LENGTH_LONG)
                                .show()
                        }
                        return@Thread
                    }

                    theta2 = result[0].toDouble()
                    pointOne =
                        Point(result[1].toFloat(), result[2].toFloat())
                    pointTwo =
                        Point(result[3].toFloat(), result[4].toFloat())
                    pointThree =
                        Point(result[5].toFloat(), result[6].toFloat())
                    val imgBase64 = result[7]
                    val decodedResult = Base64.decode(imgBase64, Base64.DEFAULT)
                    val imageBitmap =
                        BitmapFactory.decodeByteArray(decodedResult, 0, decodedResult.size)
                    runOnUiThread {
                        loading.visibility = View.GONE
                        container.visibility = View.VISIBLE
                        imageView.setImageBitmap(imageBitmap)
                        imageView.setPoints(pointOne, pointTwo, pointThree)
                        edtTheta2.setText(theta2.toString())
                    }
                }.start()
            } catch (e: FileNotFoundException) {
                e.printStackTrace()
            }
        }
    }

    @Throws(IOException::class)
    fun getBytes(inputStream: InputStream): ByteArray {
        val byteBuffer = ByteArrayOutputStream()
        val bufferSize = 1024
        val buffer = ByteArray(bufferSize)
        var len = 0
        while (inputStream.read(buffer).also { len = it } != -1) {
            byteBuffer.write(buffer, 0, len)
        }
        return byteBuffer.toByteArray()
    }

    private fun calculateN2(theta1: Double, n1: Double): Double {
        return (n1 * sin(Math.toRadians(theta1))) / sin(Math.toRadians(theta2))
    }

    private fun calculateY(N2: Double): String {
        val dumy1 = 156.53
        val dumy2 = 146.38
        return ((dumy1 * N2) - dumy2).toString()
    }
}
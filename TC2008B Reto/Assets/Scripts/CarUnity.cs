using System.Collections;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Text;
using UnityEngine;
using System.Threading;


[System.Serializable]
public struct Calle
{
    public Calle[] c;
    public Vector2 dir;
    public float speed;
}

public class CarUnity : MonoBehaviour
{
    Thread mThread;
    public string connectionIP = "127.0.0.1";
    public int connectionPort = 25001;
    IPAddress localAdd;
    TcpListener listener;
    TcpClient client;
    Vector3 receivedPos = Vector3.zero;

    public Vector3 dir;
    public GameObject CarModel;
    public float speed;

    public Calle[] calles;
    public int i;


    bool running;

    private void Start()
    {
        ThreadStart ts = new ThreadStart(GetInfo);
        mThread = new Thread(ts);
        mThread.Start();
    }

    /*void Start()
    {
        i = 0;
        python();
    }*/

    void Update()
    {
        //dir.z = 1 + (dir. * dir.y) * (1 / 2);

        dir = dir.normalized;
        transform.Translate(dir * Time.deltaTime * speed);
        //transform.position = dir;

        Quaternion newRotation = Quaternion.LookRotation(new Vector3(dir.x, 0, dir.z));
        CarModel.transform.rotation = newRotation;
    }

    public void ChangeDir(float[] vector, float s)
    {
        dir.x = vector[0];
        dir.z = vector[1];

        speed = s;

        dir = dir.normalized;
    }


    //MOCK python

    public void python()
    {
        Calle c = calles[i];
        Vector2 vtmp = c.dir;
        float[] tmp = { vtmp.x, vtmp.y };
        float t = 3.25f;
        float s = c.speed;
        i++;
        
        StartCoroutine(pythonSend(t, tmp,s));
    }

    IEnumerator pythonSend(float wait, float[] vector, float ss)
    {
        ChangeDir(vector, ss);
        yield return new WaitForSeconds(wait);
        if (i >= calles.Length)
        {
            i = 0;
        }
        python();
    }

    void GetInfo()
    {
        localAdd = IPAddress.Parse(connectionIP);
        listener = new TcpListener(IPAddress.Any, connectionPort);
        listener.Start();

        client = listener.AcceptTcpClient();

        running = true;
        while (running)
        {
            SendAndReceiveData();

        }
            speed = 0;
        
        listener.Stop();
    }

    void SendAndReceiveData()
    {
        NetworkStream nwStream = client.GetStream();
        byte[] buffer = new byte[client.ReceiveBufferSize];

        //---receiving Data from the Host----
        int bytesRead = nwStream.Read(buffer, 0, client.ReceiveBufferSize); //Getting data in Bytes from Python
        string dataReceived = Encoding.UTF8.GetString(buffer, 0, bytesRead); //Converting byte data to string

        if (dataReceived != null)
        {
            //---Using received data---
            receivedPos = StringToVector3(dataReceived); //<-- assigning receivedPos value from Python
            speed = StringToSpeed(dataReceived);
            print("received pos data, and moved the Cube!");
            dir = receivedPos.normalized;
            

            //---Sending Data to Host----
            byte[] myWriteBuffer = Encoding.ASCII.GetBytes("Hey I got your message Python! Do You see this massage?"); //Converting string to byte data
            nwStream.Write(myWriteBuffer, 0, myWriteBuffer.Length); //Sending the data in Bytes to Python
        }
        else
        {
            speed = 0;
        }
    }
    public static Vector3 StringToVector3(string sVector)
    {
        // Remove the parentheses
        if (sVector.StartsWith("(") && sVector.EndsWith(")"))
        {
            sVector = sVector.Substring(1, sVector.Length - 2);
        }

        // split the items
        string[] sArray = sVector.Split(',');

        // store as a Vector3
        Vector3 result = new Vector3(
            float.Parse(sArray[0]),
            float.Parse(sArray[1]),
            float.Parse(sArray[2]));

        return result;
    }

    public static float StringToSpeed(string sVector)
    {
        // Remove the parentheses
        if (sVector.StartsWith("(") && sVector.EndsWith(")"))
        {
            sVector = sVector.Substring(1, sVector.Length - 2);
        }

        // split the items
        string[] sArray = sVector.Split(',');

        // store as a Vector3
        float result =
            float.Parse(sArray[3]);

        return result;
    }


}

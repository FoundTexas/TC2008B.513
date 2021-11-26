using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

public class SemaforosClient : MonoBehaviour
{
    public List<Semaforo> agents;
    public List<DataSemaforo> Positions;
    public float timeToUpdate = 5.0f;
    private float timer;
    public GameObject s1,s2,s3,s4;
    bool started = false;

    IEnumerator SendData(string data)
    {
        WWWForm form = new WWWForm();
        form.AddField("bundle", "the data");
        string url = "http://localhost:8585/semaforos";
        //using (UnityWebRequest www = UnityWebRequest.Post(url, form))
        using (UnityWebRequest www = UnityWebRequest.Get(url))
        {
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(data);
            www.uploadHandler = (UploadHandler)new UploadHandlerRaw(bodyRaw);
            www.downloadHandler = (DownloadHandler)new DownloadHandlerBuffer();
            //www.SetRequestHeader("Content-Type", "text/html");
            www.SetRequestHeader("Content-Type", "application/json");

            yield return www.SendWebRequest();          // Talk to Python
            if (www.isNetworkError || www.isHttpError)
            {
                Debug.Log(www.error);
            }
            else
            {

                List<DataSemaforo> newPositions = new List<DataSemaforo>();
                string txt = www.downloadHandler.text.Replace('\'', '\"');
                txt = txt.TrimStart('"', '{', 'd', 'a', 't', 'a', ':', '[');
                txt = "{\"" + txt;
                txt = txt.TrimEnd(']', '}');
                txt = txt + '}';
                string[] strs = txt.Split(new string[] { "}, {" }, StringSplitOptions.None);
                Debug.Log("strs.Length:" + strs.Length);
                for (int i = 0; i < strs.Length; i++)
                {
                    Debug.Log(strs[i]);
                    strs[i] = strs[i].Trim();
                    if (i == 0) strs[i] = strs[i] + '}';
                    else if (i == strs.Length - 1) strs[i] = '{' + strs[i];
                    else strs[i] = '{' + strs[i] + '}';

                    Debug.Log(strs[i]);
                    DataSemaforo test = JsonUtility.FromJson<DataSemaforo>(strs[i]);
                    newPositions.Add(test);
                }

                Positions = newPositions;

                if (!started)
                {
                    started = true;
                    foreach (DataSemaforo p in Positions)
                    {
                        Semaforo a = null;

                        if (p.dir == 0) {
                            a = Instantiate(s1, this.transform.position, Quaternion.identity, null).GetComponent<Semaforo>();
                            
                        }
                        else if (p.dir == 1)
                        {
                            a = Instantiate(s1, this.transform.position, Quaternion.identity, null).GetComponent<Semaforo>();
                            a.transform.eulerAngles = new Vector3(0, 180, 0);
                        }
                        else if (p.dir == 2)
                        {
                            a = Instantiate(s1, this.transform.position, Quaternion.identity, null).GetComponent<Semaforo>();
                            a.transform.eulerAngles = new Vector3(0, -90, 0);
                        }
                        else if (p.dir == 3)
                        {
                            a = Instantiate(s1, this.transform.position, Quaternion.identity, null).GetComponent<Semaforo>();
                            a.transform.eulerAngles = new Vector3(0, 90, 0);
                        }

                        EqualSemaforo(a, p);
                        agents.Add(a);
                    }
                }
                else
                {

                    for (int i = 0; i < agents.Count; i++)
                    {
                        EqualSemaforo(agents[i], Positions[i]);
                    }
                }

            }
        }

    }

    void EqualSemaforo(Semaforo s, DataSemaforo ds)
    {
        s.Posz = ds.Posz*5;
        s.Green = ds.Green;
        s.Yellow = ds.Yellow;
        s.Red = ds.Red;
        s.Posx = ds.Posx*5;
        
    }

    // Start is called before the first frame update
    void Start()
    {
        InvokeRepeating("CallServer", 2, 1);
        /*
#if UNITY_EDITOR

        Vector3 fakePos = new Vector3(3.44f, 0, -15.707f);
        string json = EditorJsonUtility.ToJson(fakePos);

        StartCoroutine(SendData(json));
        timer = timeToUpdate;
#endif*/
    }

    void CallServer()
    {
        Debug.Log("hola");
        Vector3 fakePos = new Vector3(3.44f, 0, -15.707f);
        string json = EditorJsonUtility.ToJson(fakePos);

        StartCoroutine(SendData(json));
    }
}

using System;
using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

[Serializable]
public class car
{
    public float x;
    public float y;
    public float z;
    public bool b;
}

public class CarTest : MonoBehaviour
{
    public List<Robot> agents;
    public List<Vector3> Positions;
    public List<car> types;
    public float timeToUpdate = 5.0f;
    private float timer;
    bool started = false;
    public GameObject CarPref, CarPref2;

    IEnumerator SendData(string data)
    {
        WWWForm form = new WWWForm();
        form.AddField("bundle", "the data");
        string url = "http://localhost:8585/muliagentes";
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

                List<car> newtypes = new List<car>();

                string txt = www.downloadHandler.text.Replace('\'', '\"');
                txt = txt.TrimStart('"', '{', 'd', 'a', 't', 'a', ':', '[');
                txt = "{\"" + txt;
                txt = txt.TrimEnd(']', '}');
                txt = txt + '}';
                string[] strs = txt.Split(new string[] { "}, {" }, StringSplitOptions.None);

                for (int i = 0; i < strs.Length; i++)
                {
                    Debug.Log(strs[i]);
                    strs[i] = strs[i].Trim();
                    if (i == 0) strs[i] = strs[i] + '}';
                    else if (i == strs.Length - 1) strs[i] = '{' + strs[i];
                    else strs[i] = '{' + strs[i] + '}';

                    Debug.Log(strs[i]);
                    car test = JsonUtility.FromJson<car>(strs[i]);

                    newtypes.Add(test);
                }

                types = newtypes;

                if (!started)
                {
                    started = true;
                    foreach(car b in types)
                    {
                        Vector3 pos = new Vector3(b.x, b.y, b.z);
                        if (b.b)
                        {

                            Robot a = Instantiate(CarPref, pos * 5f, Quaternion.identity, null).GetComponent<Robot>();
                            agents.Add(a);
                        }
                        else if (b.b == false)
                        {

                            Robot a = Instantiate(CarPref2, pos * 5f, Quaternion.identity, null).GetComponent<Robot>();
                            agents.Add(a);
                        }
                    }
                }
                else
                {

                    for (int i = 0; i < agents.Count; i++)
                    {
                        car b = types[i];
                        Vector3 pos = new Vector3(b.x, b.y, b.z);
                        if (agents[i].target != pos * 5f)
                        {
                            agents[i].changeDir(pos * 5f);
                        }
                    }
                }
            }
        }

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
        Vector3 fakePos = new Vector3(3.44f, 0, -15.707f);
        string json = EditorJsonUtility.ToJson(fakePos);

        StartCoroutine(SendData(json));
    }
}

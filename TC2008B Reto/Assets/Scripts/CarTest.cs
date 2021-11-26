using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

public class CarTest : MonoBehaviour
{
    public List<Robot> agents;
    public List<Vector3> Positions;
    public float timeToUpdate = 5.0f;
    private float timer;
    bool started = false;
    public GameObject CarPref;

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

                List<Vector3> newPositions = new List<Vector3>();
                string txt = www.downloadHandler.text.Replace('\'', '\"');
                txt = txt.TrimStart('"', '{', 'd', 'a', 't', 'a', ':', '[');
                txt = "{\"" + txt;
                txt = txt.TrimEnd(']', '}');
                txt = txt + '}';
                string[] strs = txt.Split(new string[] { "}, {" }, StringSplitOptions.None);

                for (int i = 0; i < strs.Length; i++)
                {
                    strs[i] = strs[i].Trim();
                    if (i == 0) strs[i] = strs[i] + '}';
                    else if (i == strs.Length - 1) strs[i] = '{' + strs[i];
                    else strs[i] = '{' + strs[i] + '}';
                    Vector3 test = JsonUtility.FromJson<Vector3>(strs[i]);
                    newPositions.Add(test);
                }

                Positions = newPositions;

                if (!started)
                {
                    started = true;
                    foreach (Vector3 p in Positions)
                    {
                        Robot a = Instantiate(CarPref, p * 5f, Quaternion.identity, null).GetComponent<Robot>();
                        agents.Add(a);
                    }
                }
                else
                {

                    for (int i = 0; i < agents.Count; i++)
                    {
                        if (agents[i].target != Positions[i] * 5f)
                        {
                            agents[i].changeDir(Positions[i] * 5f);
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

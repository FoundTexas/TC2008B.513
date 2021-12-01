using System;
using System.Collections;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;
using UnityEngine.Networking;

public class BanderaClient : MonoBehaviour
{

    public List<GameObject> agents;
    public List<Vector3> Positions;

    public GameObject calle;
    bool started = false;

    IEnumerator SendData(string data)
    {
        WWWForm form = new WWWForm();
        form.AddField("bundle", "the data");
        string url = "http://localhost:8585/banderas";
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
                Debug.Log("strs.Length:" + strs.Length);
                for (int i = 0; i < strs.Length; i++)
                {
                    Debug.Log(strs[i]);
                    strs[i] = strs[i].Trim();

                    Debug.Log(strs[i]);
                    Vector3 test = JsonUtility.FromJson<Vector3>(strs[i]);
                    newPositions.Add(test);
                }

                Positions = newPositions;

                if (!started)
                {
                    started = true;
                    foreach (Vector3 p in Positions)
                    {
                        Vector3 vec = p;
                        vec.x *= 5;
                        vec.z *= 5;

                        GameObject a = Instantiate(calle, vec, Quaternion.identity, null);
                        agents.Add(a);
                    }
                }
                else
                {
                    for (int i = 0; i < agents.Count; i++)
                    {
                        agents[i].transform.position = Positions[i];
                    }
                }

            }
        }

    }


    // Start is called before the first frame update
    void Start()
    {
        CallServer();
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
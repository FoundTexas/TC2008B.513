using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class RadarVFC : MonoBehaviour
{
    public int NumS = 30;
    Camera cam;
    public List<GameObject> SceneObjs;

    Vector3 dir;

    bool Frustum(GameObject anyObject)
    {

        Vector3 CAMERA = cam.transform.position;
        Vector3 Camx = cam.transform.right;
        Vector3 Camy = cam.transform.up;
        Vector3 Camz = cam.transform.forward;

        float near = cam.nearClipPlane;
        float far = cam.farClipPlane;
        float wd = cam.pixelWidth;
        float ht = cam.pixelHeight;

        Vector3 objPos = anyObject.transform.position;
        Vector3 w = new Vector3(objPos.x - CAMERA.x, objPos.y - CAMERA.y, objPos.z - CAMERA.z);

        if (Vector3.Dot(w, Camz) < near || Vector3.Dot(w, Camz) > far)
        {
            return false;
        }
        else if (Vector3.Dot(w, Camy) < -ht / 2 || Vector3.Dot(w, Camy) > ht / 2)
        {
            return false;
        }
        else if (Vector3.Dot(w, Camx) < -wd / 2 || Vector3.Dot(w, Camx) > wd / 2)
        {
            return false;
        }

        return true;
    }

    // Start is called before the first frame update
    void Start()
    {
        cam = GameObject.Find("Main Camera").GetComponent<Camera>();
        for (int i = 0; i < NumS; i++)
        {
            GameObject sphere = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            float x = Random.Range(0.0f, 20.0f);
            float z = Random.Range(0.0f, 20.0f);
            sphere.transform.localPosition = new Vector3(x, 10, z);
            Rigidbody rb = sphere.AddComponent<Rigidbody>();

            float r = Random.Range(0, 1.0f);
            float g = Random.Range(0, 1.0f);
            float b = Random.Range(0, 1.0f);
            Color c = new Color(r, g, b);

            sphere.GetComponent<MeshRenderer>().material.SetColor("_Color", c);
            float scale = Random.Range(1.0f, 3.0f);
            sphere.transform.localScale = new Vector3(scale, scale, scale);
            rb.mass = scale;

            bool render = Frustum(sphere);
            SceneObjs.Add(sphere);
        }
    }
    // Update is called once per frame

    void Update()
    {
        dir.y = Input.GetAxis("Horizontal");

        cam.gameObject.transform.Rotate(dir);

        foreach (GameObject g in SceneObjs)
        {
            g.GetComponent<Renderer>().enabled = Frustum(g);
        }
        
    }
}

using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Optimization : MonoBehaviour
{
    public List<GameObject> SceneObjs;
    Camera m_cam;

    Vector3 CAMERA;
    Vector3 camX;
    Vector3 camY;
    Vector3 camZ;

    float near;
    float far;
    float with;
    float height;

    // Start is called before the first frame update
    void Start()
    {
        GameObject sphere = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        sphere.transform.localPosition = new Vector3(0, 10, 0);
        sphere.AddComponent<Rigidbody>();

        m_cam = Camera.main;
        Vector3 CAMERA = m_cam.gameObject.transform.localPosition;
        Vector3 camX = m_cam.transform.right;
        Vector3 camY = m_cam.transform.up;
        Vector3 camZ = m_cam.transform.forward;

        float near = m_cam.nearClipPlane;
        float far = m_cam.farClipPlane;
        float with = m_cam.pixelWidth;
        float height = m_cam.pixelHeight;


    }

    // Update is called once per frame
    void Update()
    {
        foreach(GameObject G in SceneObjs)
        {
            G.GetComponent<Renderer>().enabled = true;
        }
    }
}

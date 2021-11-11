using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Autormovil : MonoBehaviour
{
    public GameObject coche;
    Vector3[] geometria;
    public Vector3 A;
    public Vector3 B;
    public float t;

    Vector3[] ApplyTransform2()
    {
        Vector3 p = A + t * (B - A);
        Matrix4x4 tm = Transformations.TranslateM(p.x,p.y,p.z);
        Vector3[] transform = new Vector3[geometria.Length];

        for (int i = 0; i < geometria.Length; i++)
        {
            Vector3 v = geometria[i];
            Vector4 temp = new Vector4(v.x, v.y, v.z, 1);
            transform[i] = tm * temp;
        }

        return transform;
    }

    Vector3[] ApplyTransform(float rY)
    {
        Matrix4x4 rm = Transformations.RotateM(rY, Transformations.AXIS.AX_Y);
        MeshFilter mf = coche.GetComponent<MeshFilter>();
        Mesh mesh = mf.mesh;
        Vector3[] transform = new Vector3[mesh.vertices.Length];

        for (int i = 0; i < mesh.vertices.Length; i++)
        {
            Vector3 v = mesh.vertices[i];
            Vector4 temp = new Vector4(v.x, v.y, v.z, 1);
            transform[i] = rm * temp;
        }

        return transform;
    }

    // Start is called before the first frame update
    void Start()
    {
        t = 0;
        MeshFilter mf = coche.GetComponent<MeshFilter>();
        Mesh mesh = mf.mesh;
        geometria = mesh.vertices;
    }

    // Update is called once per frame
    void Update()
    {
        MeshFilter mf = coche.GetComponent<MeshFilter>();
        Mesh mesh = mf.mesh;
        t += 0.001f;
        mesh.vertices = ApplyTransform2();
    }

}

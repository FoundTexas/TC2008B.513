using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

[Serializable]
public class DataSemaforo
{
    public bool Green;
    public bool Yellow;
    public bool Red;
    public float Posx;
    public float Posz;
    public int dir;
}

public class Semaforo : MonoBehaviour
{
    public bool Green;
    public bool Yellow;
    public bool Red;
    public float Posx;
    public float Posz;

    public GameObject G, Y, R;

    void Update()
    {

        transform.position = new Vector3(Posx, 0, Posz);
        G.SetActive(Green);
        Y.SetActive(Yellow);
        R.SetActive(Red);
    }
}

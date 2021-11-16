using System.Collections;
using System.Collections.Generic;
using UnityEngine;


[System.Serializable]
public struct Calle
{
    public Vector2 dir;
    public float speed;
}

public class CarUnity : MonoBehaviour
{
    public Vector3 dir;
    public GameObject CarModel;
    public float speed;
    public Calle[] calles;

    public int i;

    //private Quaternion _facing;
    // Start is called before the first frame update
    void Start()
    {
        i = 0;
        //_facing = transform.rotation;
        python();
    }

    // Update is called once per frame
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

}

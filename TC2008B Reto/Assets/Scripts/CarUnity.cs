using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class CarUnity : MonoBehaviour
{
    public Vector3 dir;
    public float speed;
    public GameObject CarModel;

    private Quaternion _facing;
    // Start is called before the first frame update
    void Start()
    {
        _facing = transform.rotation;
    }
    
    // Update is called once per frame
    void Update()
    {
        //dir.z = 1 + (dir. * dir.y) * (1 / 2);
        //dir = dir.normalized;
        transform.position = dir;
        Quaternion newRotation = Quaternion.LookRotation(new Vector3(dir.x, 0, dir.z));
        CarModel.transform.rotation = newRotation;
    }
}

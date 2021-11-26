using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Robot : MonoBehaviour
{
    public Vector3[] Positions;
    public GameObject RobotModel;
    public Vector3 target;
    int iteration;
    float speed = 5;
    void Start()
    {
        /*speed = Random.Range(1, 10);
        iteration = Random.Range(0, Positions.Length);
        transform.position = Positions[iteration];
        if(iteration >= Positions.Length)
        {
            target = Positions[0];
        }
        else
        {
            target = Positions[iteration + 1];
        }
        changeDir();*/
        target = transform.position;
    }

    void Update()
    {

        if (Vector3.Distance(transform.position, target) > 0.01f)
        {
            float step = speed * Time.deltaTime;
            transform.position = Vector3.MoveTowards(transform.position, target, step);
        }
    }

    public void changeDir(Vector3 t)
    {
        target = t;

        Vector3 dir = (target - transform.position).normalized;
        Quaternion newRotation = Quaternion.LookRotation(new Vector3(dir.x, 0, dir.z));
        RobotModel.transform.rotation = newRotation;
    }
}
